import json
import argparse
from pathlib import Path
import os
import re
from Baidu_Text_transAPI import translate
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
globaltransMap = {}

def search_file(data_dir, pattern=r'\.json$'):
    root_dir = os.path.abspath(data_dir)
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if re.search(pattern, f, re.I):
                abs_path = Path(os.path.join(root, f))
                # print('new file %s' % absfn)
                yield abs_path  # abs_path

def setTransMap(j):
        msg="。"
        for dataEvent in j:
            if not (dataEvent is None or not dataEvent):
                listevent = dataEvent['list']
                if not (listevent is None or not listevent):
                    for event in listevent:
                        if event['code']==401:
                            msg += '\n' + event['parameters'][0]
                            if len(msg) > 1500:
                                trans_results = translate(msg,'auto')
                                msg="。"
                                for trans_result in trans_results:
                                  if "\\" in trans_result['src']:
                                    newstring = trans_result['dst'].replace("\\", "")
                                    globaltransMap[trans_result['src']] = trans_result['src'] + newstring
                                  else:
                                    globaltransMap[trans_result['src']] = trans_result['dst']

        trans_results =  translate(msg,'auto')     
        for trans_result in trans_results:
          if "\\" in trans_result['src']:
            newstring = trans_result['dst'].replace("\\", "")
            globaltransMap[trans_result['src']] = trans_result['src'] + newstring
          else:
            globaltransMap[trans_result['src']] = trans_result['dst']


def getTransMap(j):
    for dataEvent in j:
        if not (dataEvent is None or not dataEvent):
            listevent = dataEvent['list']
            if not (listevent is None or not listevent):
                for event in listevent:
                    if event['code']==401:
                        event['parameters'][0] = globaltransMap.get(event['parameters'][0],'')
    #outtext = json.dumps(j, indent=4, ensure_ascii=False)
    # return outtext
   
def translateFile(path,outputPath = ROOT / 'output'):
    transMap = {}
    #outputFilePath = outputPath / (path.stem + '_tran.json')
    outputFilePath = outputPath / (path.stem + '.json')
    with open(path, 'r', encoding='UTF-8') as fp:
        j = json.load(fp)
        if type(j) is list:
            setTransMap(j)
            getTransMap(j)
        else:
            events = j.get('events',[])
            for event in events:
                if not (event is None):
                  pages = event.get("pages",[])
                  setTransMap(pages)
                  getTransMap(pages)
        outtext = json.dumps(j, indent=4, ensure_ascii=False)        
        with open(outputFilePath, 'w', encoding='utf-8') as f:
          f.write(outtext)
        #print(j)
        # msg="。"
        # for dataEvent in j:
        #     if not (dataEvent is None or not dataEvent):
        #         listevent = dataEvent['list']
        #         if not (listevent is None or not listevent):
        #             for event in listevent:
        #                 if event['code']==401:
        #                     msg += '\n' + event['parameters'][0]
        #                     if len(msg) > 1500:
        #                         trans_results = translate(msg,'auto')
        #                         msg="。"
        #                         for trans_result in trans_results:
        #                           if "\\" in trans_result['src']:
        #                             newstring = trans_result['dst'].replace("\\", "")
        #                             transMap[trans_result['src']] = trans_result['src'] + newstring
        #                           else:
        #                             transMap[trans_result['src']] = trans_result['dst']

        # trans_results =  translate(msg,'auto')     
        # for trans_result in trans_results:
        #   if "\\" in trans_result['src']:
        #     newstring = trans_result['dst'].replace("\\", "")
        #     transMap[trans_result['src']] = trans_result['src'] + newstring
        #   else:
        #     transMap[trans_result['src']] = trans_result['dst']


        #h = json.load(fp)
        # for dataEvent in j:
        #     if not (dataEvent is None or not dataEvent):
        #         listevent = dataEvent['list']
        #         if not (listevent is None or not listevent):
        #             for event in listevent:
        #                 if event['code']==401:
        #                     event['parameters'][0] = transMap[event['parameters'][0]]
        # outtext = json.dumps(j, indent=4, ensure_ascii=False)
        # with open(outputFilePath, 'w', encoding='utf-8') as f:
        #   f.write(outtext)
        # print(j)

def mkdir(url):
  if not os.path.exists(url):
      os.makedirs(url)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--data', type=str, default=ROOT / 'data', help='dataset.yaml path')
  opt = parser.parse_args()
  outputPath = ROOT / 'output'
  mkdir(outputPath)
  for path in search_file(opt.data):
      translateFile(path,outputPath)