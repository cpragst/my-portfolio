import boto3
import StringIO
import zipfile
import mimetypes
import json

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')

    try:
        topic = sns.Topic('arn:aws:sns:us-east-1:956031752817:deployPortfolioTopic')

        portfolio_bucket = s3.Bucket('portfolio.cludio.net')
        build_bucket = s3.Bucket('portfoliobuild.cludio.net')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(
            Subject = 'Portfolio Deployed',
            Message = 'Portfolio deployed successfully')
    except:
        topic.publish(
            Subject = 'Portfolio Deploy Failed',
            Message = 'Portfolio not deployed due to lambda error')
        raise
    return 'ready and return'
