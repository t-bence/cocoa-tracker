mkdir package
pip install --target ./package bs4 boto3

cd package
zip -r ../my_deployment_package.zip .
cd ..
zip my_deployment_package.zip lambda_function.py