rm my_deployment_package.zip
mkdir package
pip install --target ./package bs4 boto3 requests

cd package
zip -r ../my_deployment_package.zip .
cd ..
zip my_deployment_package.zip lambda_function.py
zip -r my_deployment_package.zip ./src