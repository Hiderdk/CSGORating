
import gspread
import pandas as pd
import gspread_dataframe as gd
from oauth2client.service_account import ServiceAccountCredentials

import time
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']





GOOGLE_DRIVE_CREDENTIALS_DICT = {
  "type": "service_account",
  "project_id": "personalproject-277912",
  "private_key_id": "87d97e4f36c4257a4108b79ec4c1737b8fb94e25",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDM9pRBoJsEQZR2\n4qvuS65kcLUFQloWvwGfd/Sru4fJjTkBH3YhW1WXuS+K/sGQeTbjGPL1VK5+/Ey6\nAGXZNPMyhHNhgupDGDpKFseLMbTeIh9RURO8MSRKq4VLgLUmAQqM5zsbKtb3+bi2\nVaMdpco/2+2wJIos+wOd+SKt3/r3IyBKTcq4YRpD2XJcPog6jtdzcbstalG0wQaW\nOzvZwLWDbw4GaZmg3lwbxDE24XxD3seOiUML5EeVGaI9BZRN02i3iS9m0sXUfbMM\nXbzlpp8vHTHJqktAXrFGejNvb14sljmnsqvRWRzA+LYRH/d+N5S2+tvCoWSObE1g\nvVh8+kbvAgMBAAECggEAFIqj6iiL+1234OsFGzFSODZu1f5D5CK0KW95bIVeGFjt\n0nXSPjPr/J7ugQouNmoHkl62PtiD/S27t3/XCpv6wbXc5clxQVSExwHIcY6uQf2p\nJi+vgCgWqzXMeqLaxNp23GSc8QiWmddZEqEQ43rxraZqMxc+Z+qnqVCbj/yHfPbG\nIFL4j1nH6VBZ5s/kBOY5GM9ZaaCnNO834pO84V1iofO7OBBlzVE7UCikeKOGPG39\neA5MipS8FvaIieqwVikv10hPZtwmcgeWJ3LrJo5FRFsYZ5cJjSavcTf8VTmV9q/i\n9tHkgIGVvp+PT9ICkIto+efWFz0s4/7M6BJ7KXnUSQKBgQDwq+w7pydjdtAkLqXC\nwumiyKzL/eQezXTlM+ZihaN9nyu/NfriVz7TzGQzUtUHQSCBexa+nDFZ4mCC48AM\nK8+zb0MUS3VzXvLpUFQfq1BuM6ZdLjaD8B+hqQ8574QFvp+u/2VCibcPRbufhoDU\n7GJvNw9qYBNvrIDqlI+IgaXvtwKBgQDaBHEuAT0RmsD1MJl5Ft8utyjBfmv7JSYE\n3+7Rejjg2GtoSVFuSlfJKebCPYLt2cb9IX6C+RCr+835d1N8/dthizp/NAptkqY9\nRvAvXnAarTm5xYkUciO95IuOcbqQ92XWe8IwnOOr9/m72Wy+ZJ8gB9/1ShSN/8Eq\neCu80f7yiQKBgQC2ZGSklLo6G/oD4cJHxrWPY2vpMOGoImbbqSiJM+RCONXLlFot\nHJeFpdmuN7EwTUAYQLNtAyw3hWNE7ttFnhJLVx/MCp/ZLnUDMph+Y7ORwNzsszAn\nb1xZhKkAbC9utxeHZRBVi87K6TsW27VZKEg1JtIs+ODh+ia9IJdiiXa7IwKBgHZh\npxs17PUcNN5ub0eDFdkF94lpnjSW7VgESGdSmIPuwBO2jBL5J0XCDN04DVodwKE+\niLWRjG32otds5dae+Xqz4SWlGmx5Du+DD3SJMRIrMYcgLdj+SU4ZRXYpZwbEb3XR\naZZ/+lgspFxOKXAQrx7zZ7aHbTXVxAvNiOJUnL0RAoGBAMrK5LZ33KDD2wNE2476\nN9ge3xu168tU7fQKesBvG1vCl6wMZOmQt45BaPiGSFdqn0cZLWrAXHwSEUw9qmae\naYWZspuhMVNsP8Pnf6PhcnDp0xRZ8edfFNXIQ3Gwyi3M4NPt2BMiAwXBZGBVrNI9\nalgKZ4JT5SEqUhow1dGr8z0k\n-----END PRIVATE KEY-----\n",
  "client_email": "pythonnew@personalproject-277912.iam.gserviceaccount.com",
  "client_id": "117297756516479928088",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pythonnew%40personalproject-277912.iam.gserviceaccount.com"
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
        try: sheet = workbook.add_worksheet(title=sheet_name, rows="200", cols="50")
        except Exception as e:
            print(e)


def main_clear_sheet(sheet_name,workbook_name):

    file = gspread.authorize(credentials)
    sheet = file.open(workbook_name).worksheet(sheet_name)
    clear_sheet(sheet)
