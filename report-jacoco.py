import os
import pprint
import requests
import subprocess
import sys
import json
import itertools
from codeclimate_cidata import CI
import xml.etree.ElementTree as ET
from hashlib import sha1
from operator import itemgetter

def get_report_data(root, source_root_dir):
    sources = {}
    for package in root.iter('package'):
        sources.update(get_report_sources(package, source_root_dir))
    return sources


def get_report_sources(package, source_root_dir):
    package_name = package.attrib['name'];
    sources = {}
    for sourcefile in package.iter('sourcefile'):
        name = '/'.join([source_root_dir, package_name, sourcefile.attrib['name']])
        lines = {}
        for line in sourcefile.iter('line'):
            lineno = int(line.attrib['nr'])
            ci = int(line.attrib['ci']) # instructions hit
            mi = int(line.attrib['mi']) # instructions missed
            lines[lineno] = 1 if ci > mi else 0
        sources[name] = lines
    return sources


def create_sources_payload(reports, project_root_dir):
    sources = []

    for file, lines in reports.items():
        contents = open(file, "r", encoding="utf-8-sig").read()
        lines_total = len(contents.splitlines(True));
        header = "blob " + str(len(contents)) + "\0"
        blob_id = sha1((header + contents).encode("utf-8")).hexdigest()

        covered = sum(lines.values());
        total = len(lines);

        coverage = [None]*lines_total;
        for lineno, result in lines.items():
            coverage[lineno-1] = result

        sources.append({
            "name": os.path.relpath(file, project_root_dir),
            "blob_id": blob_id,
            "line_counts": {
                "total": total,
                "covered": covered,
                "missed": total - covered
            },
            "covered_strength": 1,
            "covered_percent": 0 if not total else covered / total,
            "coverage": json.dumps(coverage)
        })
    return sources

def make_globals(sources, root, project_root_dir):
    return {
        "run_at": root.find('sessioninfo').attrib['start'],
        #"covered_percent": 0,
        #"covered_strength": 0,
        #"line_counts": 0,
        "partial": False,
        "git": {
            "branch": shell_command("git rev-parse --abbrev-ref HEAD", project_root_dir),
            "committed_at": shell_command("git log -1 --pretty=format:%ct", project_root_dir),
            "head": shell_command("git log -1 --pretty=format:'%H'", project_root_dir),
        },
        "environment": {
            "pwd": ".",
            "reporter_version": "0.0.1"
        },
        "ci_service": CI().data(),
        "source_files": sources,
        "repo_token": os.environ.get("CODECLIMATE_REPO_TOKEN")
    }


def shell_command(command, project_root_dir):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, cwd=project_root_dir)
    exit_code = process.wait()
    if exit_code == 0:
        return process.stdout.read().decode("utf-8").strip()
    else:
        return None

def post(payload):
    response = requests.post(
        "https://codeclimate.com/test_reports",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=5
    )

    return response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: report-jacoco.py FILENAME [SOURCE_ROOT_DIR] [PROJECT_ROOT_DIR]");
        sys.exit(1);

    filename = sys.argv[1];
    source_root_dir = sys.argv[2].lstrip('/\\') if len(sys.argv) > 2 else ''
    project_root_dir = sys.argv[3].strip('/\\') if len(sys.argv) > 3 else ''


    if filename == '-':
        root = ET.fromstring(sys.stdn.read())
    else:
        tree = ET.parse(filename)
        root = tree.getroot()

    data = get_report_data(root, source_root_dir)
    data = create_sources_payload(data, project_root_dir);
    data = make_globals(data, root, project_root_dir)
    response = post(data);
    pprint.pprint(response)
    #print(data)
