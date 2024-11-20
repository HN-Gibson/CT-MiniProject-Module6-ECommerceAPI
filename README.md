# CT-MiniProject-Module6-ECommerceAPI
Creating an E-Commerce App using Flask and MySQL in Python

To run the app.py successfully, you will need to do a few things:

1. Create your own venv using the 'python -m venv gymvenv' command
2. Install the required modules to run the app using the 'pip install -r requirements.txt' command
3. Create a file named 'password.py' and set 'my_password' variable = to your db password within the created file

From there, you will be able to run the 'app.py' referencing my table models for correct table configs.

See 'app.py' detailed code to satisfy the assignment tasks.

Using the 'CT-E Commerce.postman_collection.json' configure Postman to make requests from the app for testing.

A few notes:
1. When running the postman requests, hold off on running the deletes/remove requests until you have run all others in each folder. Running the delete/remove requests before running all the others may results in not having data available and cause errors.

2. When creating an order, you do not need to input a date for the order date or delivery date. These items will be automatically generated.