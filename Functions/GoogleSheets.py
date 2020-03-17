
import gspread
import pandas as pd
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials

import time
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']




GOOGLE_DRIVE_CREDENTIALS_DICT = {
      "type": "service_account",
      "project_id": "amazing-chalice-249012",
      "private_key_id": "c43be97b2816da088a42d00d09c42614cd6c2a6f",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDIM7Ebqc9LS24l\nfjSDfCIEgZc5u31GDLeCywCN7h9Y6uvaxyamaEBxVIth6Em6zcvxcA2CbANy8wts\n9Tui8ygiT6VPR4Pn7knUA7f93D6uEpwPYxB+RtEArWUNXsCRuQAhSi4WOA6gynj9\n8BcuGHknOxlAK6x4Q7P1T491GCIAY5KkoJWhXQFAWIvQn+O29LAmOilPnCRp/IYN\nvIRoexMeiDdWZ6XhTdHtmsJR7czjI0tyEgYMFQ96I+79D2O7p2mCioW15mEPrPYe\nxmCkFqpDfqWG/LHTPtfn/c9GK+lkhwCqNsqPV0EJFlOKv9h6RBGa1Ij/yZvGQWhj\nX9lmomtvAgMBAAECggEAHI3+516vgeJG2hMno09bvL/NFX9v7UNYE1AoCpZZo0GS\nlVhNY3PAKUnxPWw3w+yhd5TPYHhOf6E50nch4+qBoW8xuV6OalC6+AH1xsAYspRV\n7P3ottIb8lhI7wDCP6ae5aCidSnWsElgu3t4musDsLxFrDjudxLVApqv7/gatWo9\nrTFTLeppJ5Cp3ZNoPyvM7PoWfugexbxJbj2EHUNblJBM4QisHzJLDXS9/exNU9sc\nYdYrWP0ZumTkcN2wYsnRKkWdd1ukyDtPgbpTEbipbrBp46WJGL8H4gCuIcpdD47C\n5QrRVdtTRzZlbCeXjYkR1wtmqfqaa6Susadc/wmAMQKBgQDvL6NMFWgFuLu6nd/Q\nGr0i2W+k9OX+1L3CgUfq0qojtsOQ+0zIdz54/lviL5mcnwHG+K8sq892+rHEtObi\nkJsChA5FD+KMVbH2IMJEaYnWnOR5xPOuxBwVF/gMigLOn9drOQVCjZw0N4l6t1Mc\nTbSciE+82G51kwo7XyQwDoH4sQKBgQDWRn/7SCFuAhCY/ln7k3Otblb8VkII4qcl\nFjMppZsDs4Yc+TjueuC92Uzwr10moqGnnPXfBvNYujOTofFlH952Pwdiu3u9uY2t\nn/JCbqzIfqKXHQRSdcPcirDJ8Ec0+tW4sdIsT2/Xd7dOjCnSq0NTKgKbjwyzsDF7\n2sD9su2uHwKBgQDVzYl0uzXO14DHodOsnBoxCpgnpdnpXpV5RkLY/xKi9f3+nQPX\nte+cDBJqLw5q2B+okidUEQhUXGeHZAV2xLgrGYv/4+EofHmlf0boDEbwFjKNPqZs\ntFQ97r0FyGAV/v96ku/Gu/rDGlnD3hdml3c47QgJ0JV8d8GPrM4WPwGjIQKBgQDN\nHTl/wkF1+/YFbl2WrESsfRY5gRy/Qq/7mW+qa0OjXGOCMrPj3a5rLaswLr49sKqM\nN31JXG7vvXaH2Rqp0cLzcExSn+PI7umHjberDiTJ3Ccp/nXXtbGi2QR4mlCfj4ms\nvlPRZM1L9eZ8A0I5zwWog2txm5LuIziLNhFOCczpwwKBgAhaJncvKzneq9os7GcL\niGmQYH+TK0rPbma9X/SBicA9Ob8c9eWVNby1hmrV/ZzyuO/M10rVFCyukWMRjYen\nFlVdTN96XxDoOyJJH9t3S8AIoz2OvGKqM8uWUYrPGwbSgdXktASqtt6OqOeo7MHx\n772WZhiIf5vXz57NrZz8wWG6\n-----END PRIVATE KEY-----\n",
      "client_email": "prettyprinted@amazing-chalice-249012.iam.gserviceaccount.com",
      "client_id": "117652482749947617507",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/prettyprinted%40amazing-chalice-249012.iam.gserviceaccount.com"
    }


credentials = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_DRIVE_CREDENTIALS_DICT, scope)
def get_sheet_names(workbook_name):
    file = gspread.authorize(credentials)
    workbook = file.open(workbook_name)
    worksheets = []
    worksheet_list =    workbook.worksheets()
    for s in  worksheet_list :
        sheet_name = str(s).split("'")[1]
        if sheet_name != 'Schedule' and sheet_name != 'Team_Names':
            worksheets.append(str(s).split("'")[1])

    return worksheets


def delete_old_sheets(workbook_name, new_game_ids):
    sheet_names = get_sheet_names(workbook_name)
    file = gspread.authorize(credentials)
    workbook = file.open(workbook_name)

    for sheet_name in sheet_names:
        if sheet_name not in new_game_ids and sheet_name != 'team_ratings' and sheet_name != 'Schedule':
            workbook.del_worksheet(workbook.worksheet(sheet_name))


def read_google_sheet(sheet_name,workbook_name):
    file = gspread.authorize(credentials)
    sheet = file.open(workbook_name).worksheet(sheet_name)
    data = sheet.get_all_values()
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)
    return df

def append_df_to_sheet(df,sheet_name,workbook_name,row_number=1,column_number=1):

    file = gspread.authorize(credentials)
    sheet = file.open(workbook_name).worksheet(sheet_name)



    #clear_sheet(sheet)
    gd.set_with_dataframe(sheet,df,row=row_number,col=column_number )

def clear_sheet(sheet_name,workbook_name):
    file = gspread.authorize(credentials)
    sheet = file.open(workbook_name).worksheet(sheet_name)
    cell_list = sheet.range('A1:AA399')
    cell_values = ["" for i in range(1,len(cell_list))]

    for i, val in enumerate(cell_values):  # gives us a tuple of an index and value
        cell_list[i].value = val  # use the index on cell_list and the val from cell_values

    sheet.update_cells(cell_list)

def create_new_sheet_if_not_exist(sheet_name,workbook_name):
    file = gspread.authorize(credentials)
    workbook = file.open(workbook_name)
    try: sheet = workbook.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = workbook.add_worksheet(title=sheet_name, rows="200", cols="50")


def main_clear_sheet(sheet_name,workbook_name):

    file = gspread.authorize(credentials)
    sheet = file.open(workbook_name).worksheet(sheet_name)
    clear_sheet(sheet)
