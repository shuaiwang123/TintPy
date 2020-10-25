import glob
import os
import re
import subprocess
import sys
import time

COREG_IFG_SUBSET = """<graph id="Graph">
  <version>1.0</version>
  <node id="Read">
    <operator>Read</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>MASTER</file>
    </parameters>
  </node>
  <node id="Read(2)">
    <operator>Read</operator>
    <sources/>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>SLAVE</file>
    </parameters>
  </node>
  <node id="Back-Geocoding">
    <operator>Back-Geocoding</operator>
    <sources>
      <sourceProduct refid="Read"/>
      <sourceProduct.1 refid="Read(2)"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <demName>SRTM 1Sec HGT</demName>
      <demResamplingMethod>BILINEAR_INTERPOLATION</demResamplingMethod>
      <externalDEMFile/>
      <externalDEMNoDataValue>0.0</externalDEMNoDataValue>
      <resamplingType>BILINEAR_INTERPOLATION</resamplingType>
      <maskOutAreaWithoutElevation>false</maskOutAreaWithoutElevation>
      <outputRangeAzimuthOffset>false</outputRangeAzimuthOffset>
      <outputDerampDemodPhase>false</outputDerampDemodPhase>
      <disableReramp>false</disableReramp>
    </parameters>
  </node>
  <node id="Enhanced-Spectral-Diversity">
    <operator>Enhanced-Spectral-Diversity</operator>
    <sources>
      <sourceProduct refid="Back-Geocoding"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <fineWinWidthStr>512</fineWinWidthStr>
      <fineWinHeightStr>512</fineWinHeightStr>
      <fineWinAccAzimuth>16</fineWinAccAzimuth>
      <fineWinAccRange>16</fineWinAccRange>
      <fineWinOversampling>128</fineWinOversampling>
      <xCorrThreshold>0.1</xCorrThreshold>
      <cohThreshold>0.15</cohThreshold>
      <numBlocksPerOverlap>10</numBlocksPerOverlap>
      <useSuppliedRangeShift>false</useSuppliedRangeShift>
      <overallRangeShift>0.0</overallRangeShift>
      <useSuppliedAzimuthShift>false</useSuppliedAzimuthShift>
      <overallAzimuthShift>0.0</overallAzimuthShift>
    </parameters>
  </node>
  <node id="Interferogram">
    <operator>Interferogram</operator>
    <sources>
      <sourceProduct refid="Enhanced-Spectral-Diversity"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <subtractFlatEarthPhase>true</subtractFlatEarthPhase>
      <srpPolynomialDegree>5</srpPolynomialDegree>
      <srpNumberPoints>501</srpNumberPoints>
      <orbitDegree>3</orbitDegree>
      <includeCoherence>false</includeCoherence>
      <cohWinAz>2</cohWinAz>
      <cohWinRg>10</cohWinRg>
      <squarePixel>true</squarePixel>
      <subtractTopographicPhase>false</subtractTopographicPhase>
      <demName>SRTM 1Sec HGT</demName>
      <externalDEMFile/>
      <externalDEMNoDataValue>0.0</externalDEMNoDataValue>
      <externalDEMApplyEGM/>
      <tileExtensionPercent/>
      <outputElevation>true</outputElevation>
      <outputLatLon>true</outputLatLon>
    </parameters>
  </node>
  <node id="TOPSAR-Deburst">
    <operator>TOPSAR-Deburst</operator>
    <sources>
      <sourceProduct refid="Interferogram"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <selectedPolarisations/>
    </parameters>
  </node>
  <node id="TOPSAR-Deburst(2)">
    <operator>TOPSAR-Deburst</operator>
    <sources>
      <sourceProduct refid="Enhanced-Spectral-Diversity"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <selectedPolarisations/>
    </parameters>
  </node>
  <node id="Write(2)">
    <operator>Write</operator>
    <sources>
      <sourceProduct refid="Subset(2)"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>OUTPUT_COREG_FILE</file>
      <formatName>BEAM-DIMAP</formatName>
    </parameters>
  </node>
  <node id="TopoPhaseRemoval">
    <operator>TopoPhaseRemoval</operator>
    <sources>
      <sourceProduct refid="TOPSAR-Deburst"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <orbitDegree>3</orbitDegree>
      <demName>SRTM 1Sec HGT</demName>
      <externalDEMFile/>
      <externalDEMNoDataValue>0.0</externalDEMNoDataValue>
      <tileExtensionPercent>100</tileExtensionPercent>
      <outputTopoPhaseBand>true</outputTopoPhaseBand>
      <outputElevationBand>true</outputElevationBand>
      <outputLatLonBands>true</outputLatLonBands>
    </parameters>
  </node>
  <node id="Subset">
    <operator>Subset</operator>
    <sources>
      <sourceProduct refid="TopoPhaseRemoval"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <sourceBands/>
      <region>0,0,0,0</region>
      <referenceBand/>
      <geoRegion>POLYGON</geoRegion>
      <subSamplingX>1</subSamplingX>
      <subSamplingY>1</subSamplingY>
      <fullSwath>false</fullSwath>
      <tiePointGridNames/>
      <copyMetadata>true</copyMetadata>
    </parameters>
  </node>
  <node id="Subset(2)">
    <operator>Subset</operator>
    <sources>
      <sourceProduct refid="TOPSAR-Deburst(2)"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <sourceBands/>
      <region>0,0,0,0</region>
      <referenceBand/>
      <geoRegion>POLYGON</geoRegion>
      <subSamplingX>1</subSamplingX>
      <subSamplingY>1</subSamplingY>
      <fullSwath>false</fullSwath>
      <tiePointGridNames/>
      <copyMetadata>true</copyMetadata>
    </parameters>
  </node>
  <node id="Write">
    <operator>Write</operator>
    <sources>
      <sourceProduct refid="Subset"/>
    </sources>
    <parameters class="com.bc.ceres.binding.dom.XppDomElement">
      <file>OUTPUT_IFG_FILE</file>
      <formatName>BEAM-DIMAP</formatName>
    </parameters>
  </node>
  <applicationData id="Presentation">
    <Description/>
    <node id="Read">
      <displayPosition x="18.0" y="24.0"/>
    </node>
    <node id="Read(2)">
      <displayPosition x="25.0" y="242.0"/>
    </node>
    <node id="Back-Geocoding">
      <displayPosition x="78.0" y="126.0"/>
    </node>
    <node id="Enhanced-Spectral-Diversity">
      <displayPosition x="207.0" y="126.0"/>
    </node>
    <node id="Interferogram">
      <displayPosition x="417.0" y="127.0"/>
    </node>
    <node id="TOPSAR-Deburst">
      <displayPosition x="550.0" y="129.0"/>
    </node>
    <node id="TOPSAR-Deburst(2)">
      <displayPosition x="465.0" y="209.0"/>
    </node>
    <node id="Write(2)">
      <displayPosition x="1009.0" y="209.0"/>
    </node>
    <node id="TopoPhaseRemoval">
      <displayPosition x="694.0" y="129.0"/>
    </node>
    <node id="Subset">
      <displayPosition x="870.0" y="130.0"/>
    </node>
    <node id="Subset(2)">
      <displayPosition x="779.0" y="213.0"/>
    </node>
    <node id="Write">
      <displayPosition x="1008.0" y="129.0"/>
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
        if "LONMIN" in line:
            LONMIN = line.split('=')[1].strip()
        if "LATMIN" in line:
            LATMIN = line.split('=')[1].strip()
        if "LONMAX" in line:
            LONMAX = line.split('=')[1].strip()
        if "LATMAX" in line:
            LATMAX = line.split('=')[1].strip()
        if "CACHE" in line:
            CACHE = line.split('=')[1].strip()
        if "CPU" in line:
            CPU = line.split('=')[1].strip()
        if re.search(r'\d{8}', line) and 'MASTER' not in line:
            SLC_INFOS.append(line.strip().split())

polygon = 'POLYGON (('+LONMIN+' '+LATMIN+','+LONMAX+' '+LATMIN+',' + \
    LONMAX+' '+LATMAX+','+LONMIN+' '+LATMAX+','+LONMIN+' '+LATMIN+'))'

if not os.path.isdir(PRJ_DIR):
    os.mkdir(PRJ_DIR)

split_dir = os.path.join(PRJ_DIR, 'split')
coreg_dir = os.path.join(PRJ_DIR, 'coreg')
if not os.path.isdir(coreg_dir):
    os.mkdir(coreg_dir)
ifg_dir = os.path.join(PRJ_DIR, 'ifg')
if not os.path.isdir(ifg_dir):
    os.mkdir(ifg_dir)

files = glob.glob(os.path.join(split_dir, '*', '*.dim'))
slaves = []
for file in files:
    if MASTER in os.path.split(file)[1]:
        master_path = file
    else:
        slaves.append(file)

for slave_path in slaves:
    index = slaves.index(slave_path) + 1
    name = os.path.split(slave_path)[1]
    print('\n[{}] Processing slave file: {}\n'.format(index, name))
    output_name = MASTER + '_' + name[0:8] + name[8:]
    xml_data = COREG_IFG_SUBSET
    xml_data = xml_data.replace('MASTER', master_path)
    xml_data = xml_data.replace('SLAVE', slave_path)
    xml_data = xml_data.replace('OUTPUT_COREG_FILE', os.path.join(coreg_dir, output_name))
    xml_data = xml_data.replace('OUTPUT_IFG_FILE', os.path.join(ifg_dir, output_name))
    xml_data = xml_data.replace('POLYGON', polygon)

    xml_name = MASTER + '_' + name[0:8] + '_coreg_ifg_subset.xml'
    xml_path = os.path.join(PRJ_DIR, xml_name)
    with open(xml_path, 'w+') as f:
        f.write(xml_data)

    args = [GPT, xml_path, '-c', CACHE, '-q', CPU]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time_start = time.time()
    stdout = process.communicate()[0]
    print('SNAP STDOUT: {}'.format(str(stdout, encoding='utf-8')))
    time_delta = time.time() - time_start
    print('Finished process in {} seconds.'.format(time_delta))
    if process.returncode != 0:
        print('Error computing with coregistration and interferogram generation of splitted slave {}\n'.format(name))
    else:
        print('Coregistration and Interferogram computation for data {}\n'.format(name))


