import os
import warnings
import numpy as np
import pandas as pd
import matplotlib 
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import platform
import seaborn as sns
import re
import streamlit as st

# 한글 폰트 설정
try:
  if platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
  else:
    rc('font', family='AppleGothic')    
except:
  pass
  
matplotlib.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

class PensionData():
  def __init__(self, filePath):
    warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)
    self.df = pd.read_csv(os.path.join(filePath), encoding='cp949')
    self.pattern1 = r'(\([^)]+\))'
    self.pattern2 = r'(\[[^)]+\])'
    self.pattern3 = r'[^A-Za-z0-9가-힣]'
    self.preprocess()
    
  def preprocessing(self, x):
    x = re.sub(self.pattern1, '', x)
    x = re.sub(self.pattern2, '', x)
    x = re.sub(self.pattern3, ' ', x)
    x = re.sub(' +', ' ', x)
    return x.strip()
    
    
  def preprocess(self):
    
    # 사업자업종코드 컬럼값이 빈 문자열인 것들은 제거
    mask = self.df['사업장업종코드'].replace({r'^\s+$': pd.NA}, regex=True).isna()
    self.df = self.df[~mask]
    self.df['사업장업종코드'] = self.df['사업장업종코드'].astype('int32')
    
    # 컬럼명들 재정의
    self.df.columns = [
      "자료생성년월", "사업장명", "사업자등록번호", "가입상태", "우편번호",
      "사업장지번상세주소", "주소", "고객법정주소코드", "고객행정주소코드",
      "시도코드", "시군구코드", "읍면동코드",
      "사업장형태구분코드 1 법인 2 개인", "업종코드", "업종코드명",
      "적용일자", "재등록일자", "탈퇴일자",
      "가입자수", "금액", "신규", "상실"
    ]
    
    # 불필요한 컬럼 제거
    df = self.df.drop([
      '자료생성년월', '우편번호', '사업장지번상세주소', '고객법정동주소코드',
      '고객행정동주소코드', '사업장형태구분코드 1 법인 2 개인', '적용일자',
      '재등록일자'
    ], axis=1)
    
    # 사업장명 cleasing
    df['사업장명'] = df['사업장명'].apply(self.preprocessing)
    
    # 탈퇴일자_연도, 탈퇴일자_월 추가
    df['탈퇴일자_연도'] = pd.to_datetime(df['탈퇴일자']).dt.year
    df['탈퇴일자_월'] = pd.to_datetime(df['탈퇴일자']).dt.month
    
    # 주소 컬럼에서 시도 부분만 새 컬럼으로 추가
    df['시도'] = df['주소'].str.split(' ').str[0]
    
    # 탈퇴한 기업들은 drop
    df = df.loc[df['가입상태'] == 1].drop(['가입상태', '탈퇴일자'], axis=1)\
           .reset_index(drop=True)
           
    # 분석하고자 하는 컬럼 추가
    df['인당금액'] = df['금액'] / df['가입자수']
    df['월급여추정'] = df['인당금액'] / 9 * 100
    df['연간급여추정'] = df['월급여추정'] * 12
    
    # 원본변경
    self.df = df

st.title("국민연금 데이터 분석")