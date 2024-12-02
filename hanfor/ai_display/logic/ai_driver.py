import logging
import time
import json
import requests
import hanfor.ai_display.logic.similarity_interface as sims
import hanfor.ai_display.logic.ai_interface as ai_interface
from flask import current_app
from reqtransformer import Requirement
import threading
import pickle
import os
from typing import List, Dict, Optional, Union
from queue import Queue

# Enable or disable debug logging
debug_enabled = False

locked_cluster = []

# File path for saving clustering results
CLUSTER_FILE_PATH = "clustering_results.pkl"


class ClusteringProgressManager:
    """Singleton class for managing clustering progress and storing results."""

    _instance = None
    clusters: Optional[List[Dict[str, Union[str, List[str]]]]] = None
    progress_bar = {"status": "not_started", "processed": 0, "total": 0}

    def __new__(cls, *args, **kwargs) -> "ClusteringProgressManager":
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.progress = None
            cls._instance.clusters = None
            cls._instance.progress_bar = {
                "status": "not_started",
                "processed": 0,
                "total": 0,
            }
        return cls._instance

    def start_clustering(self, total: int) -> None:
        """Initialize the clustering process with the total number of requirements."""
        self.progress = sims.ClusteringProgress(total=total)
        self.progress.start()

    def update_progress(self) -> None:
        """Update the progress state if the clustering process is active."""
        if self.progress:
            self.progress.update_progress()

    def get_progress_state(self) -> Dict[str, Union[str, int]]:
        """Get the current progress state of the clustering process."""
        if self.progress:
            return self.progress.get_progress_state()
        if self.progress_bar:
            return self.progress_bar
        return {"status": "ERROR", "processed": 0, "total": 0}

    def save_clusters_to_file(self) -> None:
        """Save the current clusters to a file."""
        if self.clusters is not None:
            with open(CLUSTER_FILE_PATH, "wb") as file:
                pickle.dump(self, file)
            logging.info("Clustering results saved to file.")

    @classmethod
    def load_clusters_from_file(cls) -> Optional["ClusteringProgressManager"]:
        """Load clusters from the file if it exists."""
        if os.path.exists(CLUSTER_FILE_PATH):
            with open(CLUSTER_FILE_PATH, "rb") as file:
                cls._instance = pickle.load(file)
            logging.info("Clustering results loaded from file.")
            return cls._instance
        else:
            logging.warning("No clustering file found.")
            return None


# Singleton instance for managing clustering progress
clustering_progress_manager = ClusteringProgressManager()


def start_clustering() -> None:
    clustering_progress_manager.progress_bar = {"status": "pending", "processed": 0, "total": 0}
    clustering_progress_manager.progress = None

    def run_clustering(db: object) -> None:
        requirements = extract_requirements_from_db(db)
        if not requirements:
            logging.warning("No requirements found for clustering.")
            return

        clustering_progress_manager.start_clustering(len(requirements))

        # Define and start the clustering process in a background thread
        clustering_progress_manager.clusters = sims.cluster_requirements_by_description(
            requirements, clustering_progress_manager
        )
        clustering_progress_manager.save_clusters_to_file()

    threading.Thread(target=run_clustering, args=(current_app.db,), daemon=True).start()


def get_progress_state_clustering() -> Dict[str, Union[str, int]]:
    """Get the current state of the clustering progress."""
    if debug_enabled:
        logging.debug(clustering_progress_manager.get_progress_state())
    return clustering_progress_manager.get_progress_state()


def get_clusters() -> Optional[List[Dict[str, Union[str, List[str]]]]]:
    """Retrieve the current clusters or load them from a file if not already loaded."""
    if clustering_progress_manager.clusters is None:
        clustering_progress_manager.load_clusters_from_file()
    return clustering_progress_manager.clusters


def extract_requirements_from_db(db) -> List[Dict[str, str]]:
    """Extract requirements from the database and format them for clustering, while updating the progress."""
    try:
        reqs = db.get_objects(Requirement)
    except Exception as e:
        logging.error(f"Error loading requirements: {e}")
        return []

    if not reqs:
        logging.warning("No requirements found in the database.")
        return []

    requirements = []
    total_count = len(reqs)
    processed_count = 0

    # Update progress to indicate extraction is starting
    clustering_progress_manager.progress_bar = {"status": "extracting", "processed": 0, "total": total_count}

    for key, requirement in reqs.items():
        try:
            req_type = requirement.csv_row.get("Type", None)
            if req_type == "requirement":
                requirements.append(
                    {
                        "id": requirement.csv_row.get("ID", "Unknown"),
                        "description": requirement.csv_row.get("Description", "No Description"),
                    }
                )
                # Simulate processing time
                time.sleep(0.1)

                # Increment the count of processed requirements
                processed_count += 1

                # Update the progress
                clustering_progress_manager.progress_bar = {
                    "status": "extracting",
                    "processed": processed_count,
                    "total": total_count,
                }
                if debug_enabled:
                    logging.debug(
                        "extracted: "
                        + requirement.csv_row.get("ID", "Unknown")
                        + " "
                        + requirement.csv_row.get("Description", "No Description")
                    )

        except AttributeError as e:
            logging.error(f"Error accessing attributes of requirement {key}: {e}")
            continue

    if debug_enabled:
        logging.debug(requirements)
    return requirements


def check_ai_should_formalized(requirement: Requirement) -> bool:
    return not requirement.to_dict(include_used_vars=True)["formal"]


def check_template_for_ai_formalization(rid: str) -> bool:
    """Check if the requirement is suitable for AI formalization."""
    req = current_app.db.get_object(Requirement, rid).to_dict(include_used_vars=True)
    return "has_formalization" in req["tags"]


def update(rid: str) -> None:
    """
    Update a requirement's cluster and manage AI formalization pipeline.
    """
    clusters = get_clusters()
    if not clusters:
        logging.warning("No clusters found")
        return

    if debug_enabled:
        logging.debug(f"Clusters found: {repr(clusters)}")

    if not check_template_for_ai_formalization(rid):
        logging.debug("Not suitable for AI formalization")
        return

    # Queue to manage requirements to be formalized
    req_queue = Queue()
    event = threading.Event()  # Event to signal when formalization is complete
    abort_event = threading.Event()

    def formalization_integration(formalization: dict, requirement: Requirement):
        """
        Integrate formalization into the requirement.
        """
        formalization_id, _ = requirement.add_empty_formalization()
        formatted_output = {
            str(formalization_id): {
                "id": str(formalization_id),
                "scope": formalization["scope"],
                "pattern": formalization["pattern"],
                "expression_mapping": formalization["expression_mapping"],
            }
        }
        formatted_output_json = json.dumps(formatted_output)
        url = "http://127.0.0.1:5000/api/req/"
        data = {
            "id": requirement.to_dict(include_used_vars=True)["id"],
            "row_idx": "2",
            "update_formalization": "true",
            "tags": "{}",
            "status": "Todo",
            "formalizations": formatted_output_json,
        }
        requests.post(url + "update", data=data)
        # with current_app.app_context():

    def load_requirements_to_queue(db: object) -> None:
        """
        Load all relevant requirements into a queue for processing.
        """
        for cl in clusters:
            if rid in cl:
                if cl in locked_cluster:
                    logging.info(f"Cluster {cl} is already locked, stopping the process.")
                    abort_event.set()  # Set the abort event to stop processing
                    return  # Exit the function to prevent further processing

                # Lock the current cluster
                locked_cluster.append(cl)

                for req_id in cl:
                    requirement = db.get_object(Requirement, req_id)
                    if check_ai_should_formalized(requirement):
                        req_queue.put(requirement)

        event.set()  # Signal that the queue loading is done

    def process_queue() -> None:
        """
        Process requirements from the queue using AI formalization.
        """
        while not req_queue.empty():
            if abort_event.is_set():  # Check if abort event is set
                logging.info("Aborting process queue.")
                break  # Stop processing if the abort event is set

            requirement = req_queue.get()
            logging.debug("Processing: " + requirement.to_dict()["id"])
            try:
                ai_formalization_result = ai_interface.generate_formalization(
                    requirement,
                    rid,
                )
                formalization_integration(ai_formalization_result, requirement)
            except Exception as e:
                logging.error(f"Error during AI formalization: {e}")
            finally:
                req_queue.task_done()

    # Start the loading thread
    loading_thread = threading.Thread(target=load_requirements_to_queue, args=(current_app.db,), daemon=True)
    loading_thread.start()

    def monitor_and_start_processing():
        """
        Monitor when the loading thread finishes, then start processing.
        """
        loading_thread.join()  # Wait for the loading thread to finish
        if not abort_event.is_set():  # Start processing only if not aborted (no cluster lock)
            logging.info("Starting to process the queue.")
            event.wait()  # Wait for the event to be set before starting processing
            processing_thread = threading.Thread(target=process_queue, daemon=True)
            processing_thread.start()
            processing_thread.join()  # Wait for the processing thread to finish
            for cl in clusters:
                if rid in cl:
                    locked_cluster.remove(cl)
                    logging.info(f"Finished processing cluster {cl}")
            logging.info("Finished processing the queue.")
        else:
            logging.info("Processing aborted due to cluster lock.")

    # Start monitoring and processing
    threading.Thread(target=monitor_and_start_processing, daemon=True).start()

    if debug_enabled:
        logging.debug("Update process started.")
