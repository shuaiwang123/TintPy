import glob
import os
import re
import subprocess
import sys
import time

SPLIT_ORBIT = """<graph id="Graph">
  <version>1.0</version>
  <node id="Read">
    <operator>Read</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>INPUTFILE</file>
    </parameters>
  </node>
  <node id="TOPSAR-Split">
    <operator>TOPSAR-Split</operator>
    <sources>
      <sourceProduct refid="Read"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <subswath>IW</subswath>
      <selectedPolarisations>VV</selectedPolarisations>
      <firstBurstIndex>FIRSTBURST</firstBurstIndex>
      <lastBurstIndex>LASTBURST</lastBurstIndex>
      <wktAoi/>
    </parameters>
  </node>
  <node id="Apply-Orbit-File">
    <operator>Apply-Orbit-File</operator>
    <sources>
      <sourceProduct refid="TOPSAR-Split"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <orbitType>Sentinel Precise (Auto Download)</orbitType>
      <polyDegree>3</polyDegree>
      <continueOnFail>false</continueOnFail>
    </parameters>
  </node>
  <node id="Write">
    <operator>Write</operator>
    <sources>
      <sourceProduct refid="Apply-Orbit-File"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>OUTPUTFILE</file>
      <formatName>BEAM-DIMAP</formatName>
    </parameters>
  </node>
  <applicationData id="Presentation">
    <Description/>
    <node id="Read">
            <displayPosition x="37.0" y="134.0"/>
    </node>
    <node id="TOPSAR-Split">
      <displayPosition x="162.0" y="131.0"/>
    </node>
    <node id="Apply-Orbit-File">
      <displayPosition x="320.0" y="131.0"/>
    </node>
    <node id="Write">
            <displayPosition x="455.0" y="133.0"/>
    </node>
  </applicationData>
</graph>
"""
ASSEMBLY_SPLIT_ORBIT = """<graph id="Graph">
  <version>1.0</version>
  <node id="SliceAssembly">
    <operator>SliceAssembly</operator>
    <sources>
      <sourceProduct.2 refid="ProductSet-Reader"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <selectedPolarisations>VV</selectedPolarisations>
    </parameters>
  </node>
  <node id="TOPSAR-Split">
    <operator>TOPSAR-Split</operator>
    <sources>
      <sourceProduct refid="SliceAssembly"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <subswath>IW</subswath>
      <selectedPolarisations/>
      <firstBurstIndex>FIRSTBURST</firstBurstIndex>
      <lastBurstIndex>LASTBURST</lastBurstIndex>
      <wktAoi/>
    </parameters>
  </node>
  <node id="Write">
    <operator>Write</operator>
    <sources>
      <sourceProduct refid="TOPSAR-Split"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>OUTPUTFILE</file>
      <formatName>BEAM-DIMAP</formatName>
    </parameters>
  </node>
  <node id="ProductSet-Reader">
    <operator>ProductSet-Reader</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <fileList>FILELIST</fileList>
    </parameters>
  </node>
  <applicationData id="Presentation">
    <Description/>
    <node id="SliceAssembly">
      <displayPosition x="165.0" y="61.0"/>
    </node>
    <node id="TOPSAR-Split">
      <displayPosition x="300.0" y="61.0"/>
    </node>
    <node id="Write">
      <displayPosition x="415.0" y="61.0"/>
    </node>
    <node id="ProductSet-Reader">
      <displayPosition x="15.0" y="61.0"/>
    </node>
  </applicationData>
</graph>
"""
# Getting configuration variables from conf_file
SLC_INFOS = []
with open(sys.argv[1], 'r') as f:
    for line in f.readlines():
        if 'SLC_DIR' in line:
            SLC_DIR = line.split('=')[1].strip()
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
        if re.search(r'\d{8}', line) and 'MASTER' not in line:
            SLC_INFOS.append(line.strip().split())


if not os.path.isdir(PRJ_DIR):
    os.mkdir(PRJ_DIR)


for slc_info in SLC_INFOS:
    date = slc_info[0]
    iw = slc_info[1]
    first_burst = slc_info[2]
    last_burst = slc_info[3]

    split_dir = os.path.join(PRJ_DIR, 'split')
    if not os.path.isdir(split_dir):
        os.mkdir(split_dir)

    output_dir = os.path.join(split_dir, date)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    files = glob.glob(os.path.join(SLC_DIR, 'S1*' + date + '*.zip'))

    if len(files) == 1:
        index = SLC_INFOS.index(slc_info) + 1
        print('\n[{}] SLC: {}\n'.format(index, date))

        output_name = date + '_IW' + iw + '.dim'
        output_path = os.path.join(output_dir, output_name)

        xml_data = SPLIT_ORBIT
        xml_data = xml_data.replace('IW', 'IW' + iw)
        xml_data = xml_data.replace('INPUTFILE', files[0])
        xml_data = xml_data.replace('OUTPUTFILE', output_path)
        xml_data = xml_data.replace('FIRSTBURST', first_burst)
        xml_data = xml_data.replace('LASTBURST', last_burst)

        xml_path = os.path.join(output_dir, 'split_applyorbit.xml')
    else:
        file_list = ''
        for file in files:
            if file != files[-1]:
                file_list += (file + ',')
            else:
                file_list += file
        xml_data = ASSEMBLY_SPLIT_ORBIT
        xml_data = xml_data.replace('IW', 'IW' + iw)
        xml_data = xml_data.replace('FILELIST', file_list)
        xml_data = xml_data.replace('OUTPUTFILE', output_path)
        xml_data = xml_data.replace('FIRSTBURST', first_burst)
        xml_data = xml_data.replace('LASTBURST', last_burst)

        xml_path = os.path.join(output_dir, 'assembly_split_applyorbit.xml')

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
        print('Error splitting {}.\n'.format(date))
    else:
        print('Splitting {} successfully completed.\n'.format(date))
