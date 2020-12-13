import glob
import os
import re
import subprocess
import sys
import time

PSI_EXPORT = """<graph id="Graph">
  <version>1.0</version>
  <node id="StampsExport">
    <operator>StampsExport</operator>
    <sources>
      <sourceProduct refid="Read"/>
      <sourceProduct.1 refid="Read(2)"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <targetFolder>OUTPUTFOLDER</targetFolder>
      <psiFormat>true</psiFormat>
    </parameters>
  </node>
  <node id="Read">
    <operator>Read</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>COREGFILE</file>
    </parameters>
  </node>
  <node id="Read(2)">
    <operator>Read</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>IFGFILE</file>
    </parameters>
  </node>
  <applicationData id="Presentation">
    <Description/>
    <node id="StampsExport">
      <displayPosition x="161.0" y="215.0"/>
    </node>
    <node id="Read">
      <displayPosition x="20.0" y="196.0"/>
    </node>
    <node id="Read(2)">
      <displayPosition x="29.0" y="237.0"/>
    </node>
  </applicationData>
</graph>

"""

# Getting configuration variables from conf_file
SLC_INFOS = []
with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        if 'PRJ_DIR' in line:
            PRJ_DIR = line.split('=')[1].strip()
        if 'MASTER' in line:
            MASTER = line.split('=')[1].strip()
        if "GPTBIN_PATH" in line:
            GPT = line.split('=')[1].strip()
        if "CACHE" in line:
            CACHE = line.split('=')[1].strip()
        if "CPU" in line:
            CPU = line.split('=')[1].strip()


coreg_dir = os.path.join(PRJ_DIR, 'coreg')
ifg_dir = os.path.join(PRJ_DIR, 'ifg')
export_dir = os.path.join(PRJ_DIR, 'INSAR_' + MASTER)
if not os.path.isdir(export_dir):
    os.mkdir(export_dir)

coreg_files = glob.glob(os.path.join(coreg_dir, '*.dim'))
for coreg_file in coreg_files:
    name = os.path.split(coreg_file)[1]
    ifg_file = os.path.join(ifg_dir, name)
    index = coreg_files.index(coreg_file) + 1
    print('\n[{}] Exporting pair: {}\n'.format(index, name))
    xml_data = PSI_EXPORT
    xml_data = xml_data.replace('COREGFILE', coreg_file)
    xml_data = xml_data.replace('IFGFILE', ifg_file)
    xml_data = xml_data.replace('OUTPUTFOLDER', export_dir)
    xml_name = name[0:17] + '_psi_export.xml'
    xml_path = os.path.join(PRJ_DIR, xml_name)
    with open(xml_path, 'w+') as f:
        f.write(xml_data)

    args = [GPT, xml_path, '-c', CACHE, '-q', CPU]
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time_start = time.time()
    stdout = process.communicate()[0]
    print('SNAP STDOUT: {}'.format(str(stdout, encoding='utf-8')))

    time_delta = time.time() - time_start
    print('Finished process in {} seconds.\n'.format(time_delta))

    if process.returncode != 0:
        print('Error exporting {}.\n'.format(name))
    else:
        print('StaMPS PSI export of {} successfully completed.\n'.format(name))
