from __future__ import print_function
import urllib3
import json
import os
import boto3
import pymysql.cursors

SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager()
# https://zenn.dev/fffukken/articles/86325ec0db0205
# https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, reason=None):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {
        'Status' : responseStatus,
        'Reason' : reason or "See the details in CloudWatch Log Stream: {}".format(context.log_stream_name),
        'PhysicalResourceId' : physicalResourceId or context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : noEcho,
        'Data' : responseData
    }

    json_responseBody = json.dumps(responseBody)

    print("Response body:")
    print(json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = http.request('PUT', responseUrl, headers=headers, body=json_responseBody)
        print("Status code:", response.status)


    except Exception as e:

        print("send(..) failed executing http.request(..):", e)


def lambda_handler(event, context):
  
  #Lambdaの環境変数は、CloudFormationのデプロイ時に自動で設定する
  DB_NAME = os.environ["DB_NAME"]
  DB_USER = os.environ["DB_USER"]
  DB_PASSWORD = os.environ["DB_PASSWORD"]
  DB_WRITER_ENDPOINT_ADDRESS = os.environ["DB_WRITER_ENDPOINT_ADDRESS"]

#   MATTERMOST_NAME = os.environ["MATTERMOST_NAME"]
#   MATTERMOST_USER = os.environ["MATTERMOST_USER"]
#   MATTERMOST_PASSWORD = os.environ["MATTERMOST_PASSWORD"]


  #pymysqlを利用してAuroraに接続するため、PyMySQLライブラリーを合わせてデプロイする必要がある
  conn = pymysql.connect(host=DB_WRITER_ENDPOINT_ADDRESS, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=5)
  with conn.cursor() as cur:

    #CreateTableコマンドは、mysqlの通常のコマンドと同じ。
    #cur.execute("create table service (system_id varchar(255),name varchar(255),url varchar(2048),PRIMARY KEY (system_id))")
    cur.execute("create user 'mmuser'@'%' identified by 'adminadmin'")
    # データベースはcloudformationで作ってたのでコメントアウトしてないとエラーになってしまう。
    # cur.execute("create database mattermost")
    cur.execute("grant all privileges on mattermost.* to 'mmuser'@'%'")
    # create user '{{ mattermost_user }}'@'%' identified by '{{ mattermost_password }}';
    # create database {{ mattermost_dbname }};
    # grant all privileges on {{ mattermost_dbname }}.* to '{{ mattermost_user }}'@'%';

    #S3に配置したS3ファイルをインポートするためには"LOAD DATA FROM S3 FILE"コマンドを利用する。
    # 's3://bucket-name/testData.csv'でインポートするファイルのARNを指定しています。
    # FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES の指定で、カンマ区切り・改行が\n・先頭行は無視を指定しています。
    # (system_id,name)でインポートするカラムを指定しています。
    #cur.execute("LOAD DATA FROM S3 FILE 's3://bucket-name/testData.csv' INTO TABLE service FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (system_id,name);")

    #こちらはSQLの従来通りのinsert intoコマンド。一つずつデータを入れる場合はこちらのSQLで良い。
    #cur.execute('insert into service (system_id, name) values("1", "test")')
    conn.commit()
    
    #インポートした結果はこちらのselect文で確認する。
    # cur.execute("select user, host from mysql.user")
    # cur.execute("show databases")
    # cur.execute("select * from service")
    # for row in cur:
    #   print(row)
  # うまくいかないのでcfnからの実行は諦める
  # send(event, context, SUCCESS, {})
  return {
    'statusCode': 200
  }