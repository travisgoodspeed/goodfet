
%data = dlmread('./allGearShift.csv',',');

py_shell
py('eval','import DataManage from DataManage \n dataM = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table="vue2")');
