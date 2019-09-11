toc_depth: 2

# Workflow
This example and everything that belongs to it is located in `hanfor/example`.

## Example input
Consider a CSV file `example_input.csv` which contains requirements of a realtime-system:
``` bash
ID,Description,Type
META1,This is an example for some requirements,meta
META2,Next we define some requirements,meta
REQ1,var1 is always greater than 5,requirement
REQ2,var2 is always smaller than 10,requirement
REQ3,constraint1 always holds,requirement
REQ4,constraint2 always holds,requirement
REQ5,var1 is always smaller than 5,requirement
REQ6,constraint1 and constraint2 never hold at the same time,requirement
REQ7,if var1 = True then var3 = True,requirement
REQ8,if var1 = True then var3 = False,requirement
```
In this case every row consists of the fields `ID`, `Description`, `Formalized Requirement` and `Type`.

- `ID` is a unique identifier, 
- `Description` is the description ,
- `Formalized Requirement`, is the formalization,  
- `Type`, is a type, in this example `meta` or `requirement`, where rows with type `meta` contain some meta-information
and rows with type `requirement` contain actual requirements of the module you want to formalize.

## Fire up Hanfor
1. Configure Hanfor as explained in [Configuration](/installation/configuration)
2. Start Hanfor: 
```bash
cd hanfor
python3 app.py -c example_input.csv example_tag
```
- `-c example_input.csv` specifies the csv input file we pass.
- `example_tag` is some meaningful tag you want to give this session.
If you start hanfor later with the same tag, you'll start exactly this session.

you can now reach Hanfor by visiting [http://127.0.0.1:5000](http://127.0.0.1:5000)

![Hanfor requirement overview](../img/hanfor01.png "This is how Hanfor looks like after you started it")

## Preprocessing
By default, all rows now have the status **Todo**. 
It might be the case that you want to change this for a certain set of rows to another status.

In this example we want to set every row of type `meta` to the status **Done**. 

To accomplish this we use the [Search Query Language](/usage/requirements/#search-in-requirements-table). 

1. In Hanfor, search  `:COL_INDEX_04:meta`. This will search for rows which match "meta" in the 4. coloumn (Type). You should now only see the rows of type `meta`.
2. Select all rows by clicking  **All**.
3. Click **Edit selected** and select **Done** in the field **Set status**.
4. Finally, click **Apply changes to selected requirements**

## Formalization
Order your requirement overview by **Pos** by clicking on the table column.
### REQ1
To formalize this requirement, we click on the ID **REQ1** to open then formalization-modal:

![Formalization modal](../img/hanfor02.png "This is how a formalization modal looks like")

1. Click on **+** to add a new formalization and then on **..(click to open)**
2. We now have to select a *Scope* and a *Pattern*.
- The scope is **Globally**, because the requirement states that "var1 is **always** greater than 5".
- The pattern is **it is always the case that {R} holds**.
- For **{R}** we insert the condition: `var1 > 5` 
- Set the status to **Review** and then press **save changes**.
If you save a requirement, Hanfor will automatically create the used variables and derive their type.
You can examine and even alter them in the section **Variables**, for the case that Hanfor did not derive a variable-type correctly.

![Definition of Scope and Pattern](../img/hanfor_req1_formalization.png "This is how we formalize REQ1")

The same procedure can be applied to REQ2 - REQ6

### REQ7 and REQ8
REQ7 and REQ8 are different.
Consider REQ7: `if var3 = True then var4 := True`.

- The scope is still **Globally** 
- The pattern is **it is always the case that if "{R}" holds, then "{S}" holds after at most "{T}" time units**, because in a realtime-system a variable assignment does not happen instantly, there can be delays.
- For **{R}** we insert `var3`, because the variable type is boolean.
- For **{S}** insert `var4`,
- For **{T}** we need a certain amount of time units, for example 50. We do not want to hardcode values, 
we introduce a new variable and insert `MAX_TIME`.

We end up with the following: 
``` 
Globally, it is always the case that if "var3" holds, then "var4" holds after at most "MAX_TIME" time units.
```
Save the formalization. 

You will now recognize that Hanfor automatically added a new *Tag* **Type_inference_error** to your freshly
formalized requirement. To fix that, to go the **Variables** section and open the `MAX_TIME` variable.
You see that Hanfor derived the type `bool`, but we actually want it to be of type `CONST` as the variable represents time units. Change the type and
also assign a value, for example `50`.

![Example for the `MAX_TIME` variable](../img/hanfor_var_maxtime.png "This is how you should edit the MAX_TIME variable")


For REQ8 you should have: 
``` 
Globally, it is always the case that if "var3" holds, then "!var4" holds after at most "MAX_TIME" time units.
```

## Exporting the formalized requirements.
Once you are done with all requirements, it is time to analyze them using a tool like Ultimate (TODO:ref to git).

### Preparing the export.
You might want to filter out some rows, for example, all of type `meta` or all that have a certain tag.
Again, use the [Search Query Language](/usage/requirements/#search-in-requirements-table) to select only the requirements you want.
For example, if we only rows of type `requirement` which are not on status **Todo** we search:

```
:COL_INDEX_04:requirement:AND::COL_INDEX_06::NOT:Todo
```

### Export
To export requirements, press **Tools**, then choose either `.req` or `.csv`.
If you want to analyze the requirements using Ultimate, choose **Generate .req file from (filtered) requirements table**
and then save it.

You should end up with the following:
```plain
CONST MAX_TIME IS 50.0

Input constraint1 IS bool
Input constraint2 IS bool
Input var1 IS int
Input var2 IS int
Input var3 IS bool
Input var4 IS bool

REQ1_0: Globally, it is always the case that "var1 > 5" holds
REQ2_0: Globally, it is always the case that "var2 < 10" holds
REQ3_0: Globally, it is always the case that "constraint1" holds
REQ4_0: Globally, it is always the case that "constraint2" holds
REQ5_0: Globally, it is always the case that "var1 < 5" holds
REQ6_0: Globally, it is never the case that "constraint1 && constraint2 " holds
REQ7_0: Globally, it is always the case that if "var3" holds, then "var4" holds after at most "MAX_TIME" time units
REQ8_0: Globally, it is always the case that if "var3" holds, then "!var4" holds after at most "MAX_TIME " time units
```

## Analysis using Ultimate.

### Get Ultimate
First of all you need [Ultimate](https://github.com/ultimate-pa/ultimate)

1. Install `Java JDK (1.8)` and `Maven (>3.0)`
2. Clone the repository: `git clone https://github.com/ultimate-pa/ultimate`.
3. Navigate to the release scripts `cd ultimate/releaseScripts/default/`
4. Generate a fresh binary `./makeFresh.sh`

You have now successfully forged binaries, which are located in `UAutomizer-linux/`.

### Scripts to perform the complete analysis.
We wrote scripts, which perform a complete anaylsis, including the extraction of relevant stuff.
Just copy the following three scripts, and change the directories in the head of the files where it is necessary.

- `explode_script.py`:
```python
#!/usr/bin/env python3

import argparse
import re
import sys

def get_top_operands(s):
    operands = []
    pstack = []
    last_space = None

    for i, c in enumerate(s):
        if c == '(':
            pstack.append(i)
        elif c == ')':
            if len(pstack) == 0:
                print(s)
                raise IndexError("No matching closing parens at: " + str(i))
            j = pstack.pop()
            last_space = None 
            if len(pstack) == 0:
                operands.append(s[j:i + 1])
        elif c == ' ':
            if not last_space:
                last_space = i
            else:
                if len(pstack) == 0:
                    # we have a top level operand without parenthesis
                    operands.append(s[last_space:i + 1])
                last_space = i

    if len(pstack) > 0:
        print(s)
        raise IndexError("No matching opening parens at: " + str(pstack.pop()))
    return operands


def split_and(s):
    if s.startswith('(and'):
        rtr = []
        for operand in get_top_operands(s[5:len(s) - 1]):
            rtr = rtr + split_and(operand)
        return rtr
    else:
        return [s]


parser = argparse.ArgumentParser(description='Convert (assert (and o1 o2 ...)) to (assert o1) (assert o2) (assert ...)')
parser.add_argument('-i', '--input', nargs=1, metavar='<file>', required=True, help='Specify input file')
parser.add_argument('-o', '--output', nargs=1, metavar='<file>', required=True, help='Specify output file')

try:
    args, extras = parser.parse_known_args()
except argparse.ArgumentError as exc:
    print(exc.message + '\n' + exc.argument)
    sys.exit(1)

input_script = args.input[0]
output_script = args.output[0]
if input_script == output_script:
    print('Input and output file must be different')
    sys.exit(1)

try:
    with open(input_script, encoding='utf-8') as f, open(output_script, 'w', encoding='utf-8') as o:
        for line in f.readlines():
            if line.startswith("(assert (!"):
                m = re.search('\(assert \(! (.*?) :named (.*?)\)\)', line)
                formula = m.group(1)
                if formula == 'true':
                    continue
                name = m.group(2)
                asserts = split_and(formula)
                if len(asserts) == 1:
                    o.write('(assert (! {} :named {}))\n'.format(asserts[0], name))
                else:
                    i = 0
                    for sub in asserts:
                        o.write('(assert (! {} :named {}))\n'.format(sub, name + '_' + str(i)))
                        i = i + 1
            else:
                o.write(line)
except FileNotFoundError as exc: 
    print('Did not find ' + input_script)
    print('Arguments were '+ str(args))
    sys.exit(1)
```

- `extract_vac_reasons.sh`,  used to extract reasons why a requirement is vacuous.
```bash
#!/bin/bash
# script that prepares a .req file with the reasons for vacuity for a known vacuous requirement
# start it from the initial dump directory

orig_req_file="${1}"
ultimate_log="${2}"

# This is what you have to change:
requirement_repo="/storage/repos/your_requirement_repo"
ultimate_repo="/storage/repos/ultimate"
explode="${requirement_repo}/explode_script.py"
ultimate_dir="${ultimate_repo}/releaseScripts/default/UAutomizer-linux"

# Below here you do not have to change anything, except you know what you are doing.
tmp_dump_dir="dump-ss"
dump_dir="dump"

function check_params(){
    if [[ $PWD != *"$dump_dir" ]]; then
        echo "Not in directory $dump_dir"
        exit 1;
    fi
}

function parse_results(){
    mapfile -t results < <( grep -oP ' - .*Result.*' "$ultimate_log" | grep 'is vacuous' | grep -oP 'Requirement .* is' | cut -d ' ' -f 2 )
}

function print_results(){
    if [ ${#results[@]} -eq 0 ]; then
        echo "No vacuous requirements remaining! This is unexpected. Check $reduced_req_file and $ultimate_log"
        return 1
    else
        echo "${#results[@]} requirements still vacuous: ${results[@]}"
		return 0
    fi
}


function get_involved_reqs(){
    local reason_file="$req_id.vac"
    local tmp_file="$req_id.tmp"
    local regexpr=""

    if readlink -e "$tmp_file" > /dev/null ; then
        echo "$tmp_file still exists"
        exit 1
    fi

    for smt_file in $smt_file_pref
    do
        echo "Considering $smt_file"
        tmp_smt_file="${smt_file}.lbe"
        eval "$explode -i $smt_file -o $tmp_smt_file"
        if ! readlink -e "$tmp_smt_file" > /dev/null ; then
            echo "$explode -i $smt_file -o $tmp_smt_file did not produce the expected output, something is wrong"
            echo "The current folder is $PWD"
            exit 1
        fi
        sed -i 's/(get-interpolants.*/(get-unsat-core)/g' "$tmp_smt_file"
        sed -i '/\:interpolant-check-mode/d' "$tmp_smt_file"
        sed -i '/\:proof-transformation/d' "$tmp_smt_file"
        sed -i '/\:array-interpolation/d' "$tmp_smt_file"
        # You can check if z3 complains about something in the file
        #../z3 "$tmp_smt_file"
        for i in `"$ultimate_dir/z3" "$tmp_smt_file" | grep -A 1 -P ^unsat$ | tail -n +2 | sed 's/(//g' | sed 's/)//g'`; do grep "$i" "$tmp_smt_file"; done | grep -oP 'SysRS_\w+_\d+_\d+' | sort | uniq >> "$tmp_file"
        rm "$tmp_smt_file"
    done

    sort "$tmp_file" | uniq > "$reason_file"
    rm "$tmp_file"

    if ! grep -q "$req_id" "$reason_file" ; then
        echo "TODO: if the tmp_file does not contain the req_id in the unsat core, we need to remove reasons for infeasibility and try again"
        return 1
    fi

    echo "Found `wc -l $reason_file | cut -d " " -f 1` involved reqs"
    tr '[:space:]' ' ' < "$reason_file"
    echo ""

    for i in `cat $reason_file` ; do regexpr+="\|$i.*$"; done
    rm "$reason_file"
    sed "/CONST.*$\|Input.*$""$regexpr/!d" "$orig_req_file" > "$reduced_req_file"
    return 0
}

function run_ultimate_ss(){
    rm -r "$tmp_dump_dir"
    mkdir "$tmp_dump_dir"
    ultimate_log=`readlink -f "${tmp_dump_dir}/ultimate.log"`
    echo "Running Ultimate"
    java -Dosgi.configuration.area=config/ \
    -Xmx10G \
    -jar plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar \
    -tc "${ultimate_repo}/trunk/examples/toolchains/ReqCheck.xml" \
    -s "${requirement_repo}/reqanalyzer-nonlin.epf" \
    -i "${dump_dir}/$reduced_req_file" \
    --pea2boogie.check.consistency false \
    --pea2boogie.check.rt-inconsistency false \
    --traceabstraction.dump.smt.script.to.file true \
    --traceabstraction.to.the.following.directory="${tmp_dump_dir}/" \
    > "$ultimate_log"
}

check_params
parse_results
initial_results="${results[@]}"
echo "Processing ${#results[@]} vacuous requirements"
for i in ${initial_results[@]}
do
    req_id="$i"
    reduced_req_file="$req_id.vac.req"
    echo "----"
    echo "Processing $req_id"
    smt_file_pref="*VAC*_"`echo "$req_id" | cut -d "_" -f 3-`"_*.smt2"

    if ! get_involved_reqs ; then
      continue
    fi

    pushd "$ultimate_dir" > /dev/null

    run_ultimate_ss
    parse_results
    if print_results ; then
      pushd "$tmp_dump_dir" > /dev/null
      get_involved_reqs
      echo "Writing $reduced_req_file"
      cp "$reduced_req_file" "../${dump_dir}/"
      cp "$reduced_req_file" "../"
      popd > /dev/null
    fi

    popd > /dev/null

    echo "Finished $req_id"
    echo ""
done
```

- `run_complete_analysis.sh`, used to run the complete analysis.
```bash
#!/bin/bash
# script that runs all the various requirement analysis scripts and moves files around in the matching directories


### Default settings
# The requirement file is an argument passed to this script.
req_file="$1"
# This is the path to the repository, which contains the requirements-folder
req_repo_folder="/path/to/req/repo"
# This is the path to the requirements-folder
req_folder="${req_repo_folder}/reqs"
# Path to the vacuity extractor script.
vac_extractor="${req_repo_folder}/extract_vac_reasons.sh"
# Path to the Ultimate repository.
ultimate_repo_folder="/storage/repos/ultimate"
# Path to Ultimate Automizer (remember those binaries we created earlier? that's what you want!).
automizer_folder="${ultimate_repo_folder}/releaseScripts/default/UAutomizer-linux"
# Don't touch this, unless you know what you are doing.
reqcheck_toolchain="${ultimate_repo_folder}/trunk/examples/toolchains/ReqCheck.xml"
reqcheck_settings="${ultimate_repo_folder}/trunk/examples/settings/reqanalyzer/reqanalyzer-nonlin.epf"
testgen_toolchain="${ultimate_repo_folder}/trunk/examples/toolchains/ReqToTest.xml"
testgen_settings="${ultimate_repo_folder}/trunk/examples/settings/ReqToTest.epf"
# The time how long a single assertion is checked.
timeout_per_assertion=900
# The amount of requirements which are checked together for RT-inconsistency.
# Careful with this parameter, it will blow up the amount of checks really fast.
rt_inconsistency_range=2

### Functions
function prompt {
  read -p "${1} [y/N]" -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]] ; then
      return 0
  fi
  return 1
}

function test_if_cmd_is_available {
  local cmd_path=`command -v "$@"`
  [ $? -eq 0 ] || { echo >&2 "I require $@ but it's not installed. Aborting."; exit 1; }
  if ! [[ -f "$cmd_path" && -x $(realpath "$cmd_path") ]]; then
    echo >&2 "I require $@ but it's not executable. Aborting."; exit 1;
  fi
}

function exitOnFail {
  "$@"
  local status=$?
  if [ $status -ne 0 ]; then
              echo "$@ failed with $1"
              exit $status
  fi
  return $status
}

function run_reqcheck {
  pushd "$automizer_folder" > /dev/null

  local dump_folder="$PWD""/dump-"`basename $req_file`

  if ! readlink -e "$PWD/plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar" > /dev/null ; then
    echo "$PWD does not contain Ultimate binaries"
    exit 1
  fi

  if readlink -e "$dump_folder" > /dev/null ; then
    echo "Found old dump directory $dump_folder"
    if prompt "Should I delete the directory?" ; then
      rm -r "$dump_folder"
    else
      exit 1
    fi
  fi

  if readlink -e "$reqcheck_log" > /dev/null ; then
    echo "Logfile $reqcheck_log already exists"
    if prompt "Overwrite?" ; then
        rm "$reqcheck_log"
    else
        exit 1
    fi
  fi

  echo "Analyzing $req_file"
  echo "Using log file $reqcheck_log"
  mkdir "$dump_folder"

  java \
  -Dosgi.configuration.area=config/ \
  -Xmx100G \
  -Xss4m \
  -jar plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar \
  -tc "$reqcheck_toolchain" \
  -s "$reqcheck_settings" \
  -i "$req_file" \
  --core.print.statistic.results false \
  --traceabstraction.dump.smt.script.to.file true \
  --traceabstraction.to.the.following.directory="$dump_folder" \
  --traceabstraction.limit.analysis.time $timeout_per_assertion \
  --pea2boogie.always.use.all.invariants.during.rt-inconsistency.checks true \
  --pea2boogie.check.vacuity true \
  --pea2boogie.check.consistency true \
  --pea2boogie.check.rt-inconsistency true \
  --pea2boogie.report.trivial.rt-consistency false \
  --pea2boogie.rt-inconsistency.range $rt_inconsistency_range \
  > "$reqcheck_log"

  popd > /dev/null


  ### Postprocess results with vacuity extractor
  if [ ! -f "$reqcheck_log" ]; then
    echo "File $reqcheck_log was not created; aborting."
    exit 1
  fi

  echo "Extracting results to $reqcheck_relevant_log"
  grep "  -" "$reqcheck_log" | grep -v "StatisticsResult" | grep -v "ReqCheckSuccessResult" \
  > "$reqcheck_relevant_log"

  if grep -q "vacuous" "$reqcheck_relevant_log" ; then
    echo "Analyzing reasons for vacuity"
    pushd "$dump_folder" > /dev/null
    exitOnFail ${vac_extractor} "$req_file" "$reqcheck_log"
    mv *.vac.req "$log_folder""/"
    popd > /dev/null
  else
    echo "No vacuities found"
  fi
}

function run_testgen {
  echo "Using log file $testgen_log"

  pushd "${automizer_folder}" > /dev/null
  if ! readlink -e "$PWD/plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar" > /dev/null ; then
    echo "$PWD does not contain Ultimate binaries"
    exit 1
  fi

  java \
  -Dosgi.configuration.area=config/ \
  -Xmx100G \
  -Xss4m \
  -jar plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar \
  -tc "$testgen_toolchain" \
  -s "$testgen_settings" \
  -i "$req_file" \
  --core.print.statistic.results false \
  --rcfgbuilder.simplify.code.blocks false \
  --rcfgbuilder.size.of.a.code.block LoopFreeBlock \
  --traceabstraction.limit.analysis.time $timeout_per_assertion \
  --rcfgbuilder.add.additional.assume.for.each.assert false \
  > "$testgen_log"

  sed -ne '/--- Results ---/,$p' "$testgen_log" > "$testgen_relevant_log"

  popd > /dev/null
}

### Check parameters
for i in "$ultimate_repo_folder" "$automizer_folder" "$req_folder" ; do
  if [ ! -d "$i" ]; then
    echo "Folder $i does not exist"
    exit 1
  fi
done

for i in "$req_file" "$reqcheck_toolchain" "$reqcheck_settings" "$testgen_toolchain" "$testgen_settings" ; do
  if [ ! -f "$i" ]; then
    echo "File $i does not exist"
    exit 1
  fi
done

test_if_cmd_is_available ${vac_extractor}

req_file=`readlink -f "$req_file"`
reqcheck_log="$req_folder""/"`basename $req_file`".log"
testgen_log="$req_folder""/"`basename $req_file`".testgen.log"

req_file_name=$(basename -- "$req_file")
req_file_name="${req_file_name%.*}"

log_folder="$req_folder""/logs/""$req_file_name"
reqcheck_relevant_log="$log_folder""/""$req_file_name"".req.relevant.log"
testgen_relevant_log="$log_folder""/""$req_file_name"".req.testgen.log"


### Prepare folders
if [ ! -d "$log_folder" ]; then
  if prompt "$log_folder does not exist, should I create it?" ; then
    mkdir -p "$log_folder"
  else
    exit 2
  fi
fi


### Start running actual tools
echo "Running ReqChecker"
exitOnFail run_reqcheck

echo "Running TestGen"
exitOnFail run_testgen


### Print result summary
cat<<EOF
Results for $1
Test-cases:            $testgen_relevant_log
ReqChecker results:    $reqcheck_relevant_log
Reasons for vacuity:   `grep -q "vacuous" "$reqcheck_relevant_log" && ls ${log_folder}/*.vac.req`
Full ReqCheck logfile  $reqcheck_log
Full TestGen logfile   $testgen_log
EOF

exit 0
```

### Use Ultimate
We now simply execute the `run_complete_analysis.sh` script.
``` bash
$ cd hanfor/example
$ ./run_complete_analysis.sh example_input.req
```
This will fire up Ultimate and run an analysis. The analysis checks for rt-inconsistency and vacuity and logs are be generated: 

- `hanfor/example/example_input.req.log`
- `hanfor/example/example_input.req.testgen.log`
- `hanfor/example/logs/example_input/example_input.req.relevant.log`
- `hanfor/example/logs/example_input/example_input.req.testgen.log`

### Evaluate

In `hanfor/example/example_input.req.log` we can see that Ultimate reports: 
``` 
 --- Results ---
 * Results from de.uni_freiburg.informatik.ultimate.pea2boogie:
  - RequirementInconsistentErrorResult: Requirements set is inconsistent.
    Requirements set is inconsistent. Some invariants are already infeasible. Responsible requirements: REQ6_0, REQ3_0, REQ4_0
```
Now, if we investigate REQ3, REQ4 and REQ6:

``` 
REQ3_0: Globally, it is always the case that "constraint1" holds
REQ4_0: Globally, it is always the case that "constraint2" holds
REQ6_0: Globally, it is never the case that "constraint1 && constraint2 " holds
```
We directly see what the problem is: On one hand, our invariants demand that `constraint1` and `constraint2` always holds,
but on the other hand there is another invariant which demands that `constraint1` and `constraint2` never hold at the same time.
Think about this as:
```
constraint1 && constraint2 && ((constraint1 && !constraint2) || (!constraint1 && constraint2))
```
this is clearly unsatisfiable.

### Alter your requirements
We now found an inconsistency in our requirements, that has to be fixed. 
Let's assume you review your requirements and you recognize `REQ4` was defined wrong in the csv,
where `REQ4,constraint2 always holds,requirement` should be `REQ4,constraint2 never holds,requirement`.
While reading over the requirements, you also recognize that `REQ1` and `REQ5` collide and you find out that `REQ5` shall be deleted.

When we apply this changes, we end up with the following changes: 

 - alter `REQ4,constraint2 always holds,requirement` to `REQ4,constraint2 never holds,requirement`
 - remove `REQ5`
 
and our csv file now looks as follows: 

``` bash
ID,Description,Type
META1,This is an example for some requirements,meta
META2,Next we define some requirements,meta
REQ1,var1 is always greater than 5,requirement
REQ2,var2 is always smaller than 10,requirement
REQ3,constraint1 always holds,requirement
REQ4,constraint2 never holds,requirement
REQ6,constraint1 and constraint2 never hold at the same time,requirement
REQ7,if var1 = True then var3 = True,requirement
REQ8,if var1 = True then var3 = False,requirement
```

### Time for a new revision.
We altered our requirements, we now need to create a new revision in Hanfor and change our formalizations.
Execute: 

``` 
$ cd hanfor
$ python3 app.py -r -c example/example_input.csv example_tag
```

- Hanfor will then ask: **"Which revision should I use as a base?"**,
we choose `revision_0` (as it is the only one, usually you want your latest revision).

- Then, Hanfor asks **Should I use the csv header mapping from base revision?**,
as we did not change the csv header, we just keep the current one.

A quick recap what happens when creating a revision:
- New requirements get the tag `revision_0_to_revision_1_new_requirement`
- Changed requirements get the tag `revision_0_to_revision_1_data_changed` and `revision_0_to_revision_1_description_changed`
- Requirements where the formalization migrated to the new revision get the tag `revision_0_to_revision_1_migrated_formalized`

We now have to alter the requirements which have changed, that's only `REQ4`. 
Open the formalization of `REQ4` and correct it to `Globally, it is never the case that "constraint2" holds`.

### Ultimate Analysis #2
1. Export your requirements as before
2. Run Ultimate on them

TODO.
