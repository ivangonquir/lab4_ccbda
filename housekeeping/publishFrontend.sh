#!/bin/bash

MY_TEAM=team4-5
BUCKET_NAME="next-js-${MY_TEAM}.2026-spring.ccbda.upc.edu"
AWS_REGION="eu-north-1"

cd frontend
npm install --save-dev dotenv-cli
npx env-cmd -f ../.env.cloud npm run build

aws s3 mb s3://${BUCKET_NAME} --region ${AWS_REGION}
aws s3 website s3://${BUCKET_NAME} --index-document index.html --error-document 404.html
aws s3api put-public-access-block --bucket ${BUCKET_NAME} --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=true
aws s3 sync ./out s3://${BUCKET_NAME} --delete
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
    --cloud-front-origin-access-identity-config "CallerReference=$(date +%s),Comment=OAI-for-my-nextjs-app-bucket" \
    | jq -r '.CloudFrontOriginAccessIdentity.Id')
S3_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ${OAI_ID}"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF
)
aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy ${S3_POLICY}

DISTRIBUTION_CONFIG=$(cat <<EOF
{
  "CallerReference": "'$(date +%s)'",
  "Comment": "CloudFront distribution for my Next.js frontend app",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-Origin",
        "DomainName": "${BUCKET_NAME}.s3.${AWS_REGION}.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/${OAI_ID}"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-Origin",
    "ViewerProtocolPolicy": "allow-all",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": { "Forward": "none" }
    },
    "MinTTL": 3600
  },
  "CustomErrorResponses": {
  "Quantity": 2,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponseCode": "200",
        "ResponsePagePath": "/index.html"
      },
      {
        "ErrorCode": 403,
        "ResponseCode": "200",
        "ResponsePagePath": "/400.html"
      }
    ]
  }
}
EOF
)

CLOUDFRONT_ID=$(aws cloudfront create-distribution --distribution-config ${DISTRIBUTION_CONFIG} \
   | jq -r '.Distribution.Id')

aws cloudfront get-distribution --id ${CLOUDFRONT_ID} | jq -r '.Distribution.Status,.Distribution.DomainName'