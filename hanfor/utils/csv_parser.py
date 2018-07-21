import csv
import logging

from hanfor import db
from hanfor.models import Requirement, CsvEntry, CsvHeaderEntry
from hanfor.utils.choice import choice


class CsvParser:
    def __init__(self):
        self.csv_meta = {
            'dialect': None,
            'fieldnames': None,
            'headers': list(),
            'id_header': None,
            'desc_header': None,
            'formal_header': None,
            'type_header': None,
        }
        self.csv_headers = dict()
        self.csv_all_rows = None
        self.requirements = list()

    def create_from_csv(self, csv_file, input_encoding='utf8', base_revision_headers=None):
        """ Create a RequirementCollection from a csv file, containing one requirement per line.
        Ask the user which csv fields corresponds to which requirement data.

        :param csv_file:
        :type csv_file:
        :param input_encoding:
        :type input_encoding:
        """
        self.load_csv(csv_file, input_encoding)
        self.select_headers(base_revision_headers)
        self.store_csv_headers_to_db()
        self.parse_csv_rows_into_requirements()

    def load_csv(self, csv_file, input_encoding):
        """ Reads a csv file into `csv_all_rows`. Stores csv_dialect and csv_fieldnames in `csv_meta`

        :param csv_file: Path to csv file.
        :type csv_file: str
        :param input_encoding: Encoding of the csv file.
        :type input_encoding: str
        """
        logging.info('Load CSV Input from : {}'.format(csv_file))
        with open(csv_file, 'r', encoding=input_encoding) as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(2048), delimiters='\t')
            except csv.Error:
                logging.info("Could not guess .csv dialect, assuming defaults")
                csv.register_dialect('ultimate', delimiter=',')
                dialect = 'ultimate'
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            self.csv_meta['dialect'] = dialect
            self.csv_all_rows = list(reader)
            self.csv_meta['fieldnames'] = reader.fieldnames
            self.csv_meta['headers'] = list(self.csv_all_rows[0].keys())

    def select_headers(self, base_revision_headers=None):
        """ Ask the users, which of the csv headers correspond to our needed data.

        """
        use_old_headers = False
        if base_revision_headers:
            print('Should I use the csv header mapping from base revision?')
            use_old_headers = choice(['yes', 'no'], 'yes')
        if base_revision_headers and use_old_headers == 'yes':
            self.csv_meta['id_header'] = base_revision_headers['csv_id_header']
            self.csv_meta['desc_header'] = base_revision_headers['csv_desc_header']
            self.csv_meta['formal_header'] = base_revision_headers['csv_formal_header']
            self.csv_meta['type_header'] = base_revision_headers['csv_type_header']
        else:
            print('Select ID header')
            self.csv_meta['id_header'] = choice(self.csv_meta['headers'], 'ID')
            print('Select requirements description header')
            self.csv_meta['desc_header'] = choice(
                self.csv_meta['headers'],
                'System Requirement Specification of Audi Central Connected Getway'
            )
            print('Select formalization header')
            self.csv_meta['formal_header'] = choice(self.csv_meta['headers'] + ['Add new Formalization'],
                                                          'Formal Req')
            if self.csv_meta['formal_header'] == 'Add new Formalization':
                self.csv_meta['formal_header'] = 'Hanfor_Formalization'
                self.csv_meta['headers'].append(self.csv_meta['formal_header'])
            print('Select type header.')
            self.csv_meta['type_header'] = choice(self.csv_meta['headers'], 'RB_Classification')

    def store_csv_headers_to_db(self):
        # Create missing headers in the DB.
        # Store the headers in csv_headers dict.
        for order_index, header_name in enumerate(self.csv_meta['headers']):
            csv_header = CsvHeaderEntry().query.filter_by(text=header_name, order=order_index).first()
            if csv_header is None:
                csv_header = CsvHeaderEntry(text=header_name, order=order_index)
                db.session.add(csv_header)
                db.session.commit()
            self.csv_headers[header_name] = csv_header

    def parse_csv_rows_into_requirements(self):
        """ Parse each row in csv_all_rows into one Requirement.

        """
        for index, row in enumerate(self.csv_all_rows):
            requirement = Requirement(
                rid_header=self.csv_headers[self.csv_meta['id_header']],
                description_header=self.csv_headers[self.csv_meta['desc_header']],
                formalization_header=self.csv_headers[self.csv_meta['formal_header']],
                type_header=self.csv_headers[self.csv_meta['type_header']],
                pos_in_csv=index
                #description=row[self.csv_meta['desc_header']],
                #type_in_csv=row[self.csv_meta['type_header']],
                #csv_row=row,
            )
            db.session.add(requirement)
            for csv_entry_header_name, csv_entry_string in row.items():
                entry = CsvEntry(
                    header=self.csv_headers[csv_entry_header_name],
                    requirement=requirement,
                    text=csv_entry_string
                )
                db.session.add(entry)

            logging.info('Added requirment with ID:`{}`'.format(requirement.id))
        db.session.commit()
