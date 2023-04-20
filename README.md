# E-Commerce Application

URL: https://e-commerce-app-l7zh.onrender.com/

## Programming language and framework
When I did some research in Render's docs, I saw the quickstart options and the most familiar language in these options was Python for me. So, I continued with it. There are 3 frameworkds with Python that Render supports. When I inspected them one by one, the most basic one was Flask. Also, I did some research on Internet and figured out that working with MongoDB from Flask is way simpler than other frameworks. Since I am not very familiar with web applications, I decided to continue with most basic one.

## Design Decisions
For database connection and operations, I used MongoDB library for python, **pymongo**. At the beginning of application, I created a Mongo client with my credentials and I fetch my database, **flask_db** as db. Then, I did all database operations by using this **db** object. 

In my database, I have two collections, **users** and **items**. In users collection, each user has username, password and is_admin fields. is_admin is a boolean value which indicates whether user is an admin or not. In items collection, all items has name, description, category, price, seller, image, ratings, avg_rating and reviews fields. There are additional fields for **Clothing** as size and color, for **Monitor** and **Computer Components** as specification. In ratings and reviews fields, ratings and reviews are stored with the current user's username.

There are endpoints and pages for each operation. Page templates are in templates folder. There is a base.html file which is derived by every page. This base page has navigation bar in the web application. By deriving this page in all pages, I avoided from making changes in every page when I add something to navigation bar. In index page, index.html, all items are listed with their descriptions and average ratings. For item page, item.html, there is a template and it is filled by the web application by fetching information about item from database with item's id. There are adding and removing item and user pages. They are only visible to admins. For adding pages, there are forms to submit. When they submitted, post request is parsed by related endpoint and recorded into the corresponding collection, items or users. In user page, user.html, there is a template and its filled by the web application by fetching information about user from database with user id.

## How to login
At the top right of each page, there is a login button which redirects to login page. A regular user does not need a password. Only username is enough to log a user in. For admins, they need to authorize with their passwords. The login button turns out to logout button when any user is logged in. It clears the currently logged in user. Users in the application is listed below:
* Username: bugra (Admin)
  Password: bugra123
* Username: admin1 (Admin)
  Password: admin1
* Username: notadmin1 (Regular user)
* Username: notadmin2 (Regular user)

## How to use the application

To run the application, 'flask run' command should be executed in command line.

In index page, all items are listed. There is a category filter below the navigation bar. When any category is selected and 'Filter' button is clicked, items with selected category is listed. When an item's name is clicked, the website is redirected to item's page. There are information about the item, average rating and reviews. Reviews are listed at the bottom. Also, there are 'Rate' and 'Leave a comment' sections. If a user is logged in, the user can rate or review the item. Else, the website is redirected to login page. Each user can rate the item or leave a review. If any user is not logged in, only home page is visible. If a regular user logged in, 'Profile' button is added to navigation bar. When it is clicked, the website is redirected to currently user's page. In this page, username of the user, user's role(regular user or admin), average rating and reviews written to all items are listed. Reviewed items can also be accessed from this page by clicking their names in 'Reviews' section. When a user logged in as an admin, 'Add Item', 'Add User', 'Remove Item' and 'Remove User' buttons appears in the navigation bar. In 'Add Item' page, there is a from to add an item. At the beginning, it asks for all common fields for each item. In category part, if 'Clothing' is selected it asks for also size and color. For 'Monitor' and 'Computer Components' category, it also asks for additional fields. In 'Add User' page, it asks for a username and whether the user is admin or not. If 'Yes' box is checked, it also asks for a password. If an already existing username is entered, it denies the operation and reloads the page. In 'Remove Item' page, all items are listed and a checkbox is attached for each item. Filtering by category is still valid here. For the items to be removed, their checkboxes should be clicked. At the end of page, there is a 'Remove' button. When it is clicked, selected items are removed. For 'Remove User' page, the same logic applies here but the admins can not be removed. 

