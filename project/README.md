# CSV Manager

## Video Link
https://youtu.be/drUne2nf5BU

## Before (Planning and TODO)
Skip to the "After" section to see the full documentation

#### Overview
So, I want to make a webapp that allows you to import csv files, and then display them and stuff, and maybe even be able to join them, like you would in a database.
I think I'd like to have something like a preset; i.e. if you have a sports team, and you want to see who scored the highest. I also want to have some sort of JS
functionality, but I'm not sure how I'm going to do that yet.

I'd love to find someone way to integrate an API, but I'm not sure how or why I would do that.

I want everything listed below to be the "main body" of the application, but I'd also like some extra smaller features, like little notifications, or an option to
change your password.

#### app.py
This will of course maintain all of the routes for my application, and I'll update them here as I go along.

/
/loaded_file
/index
/search
/login
/register
/upload_file
/logout

#### index.html
Nav Bar with the elements (Home Page):
Home
Search File:
Logout:
Upload File:

Nav Bar with the elements (Login Page)
Register:
Login:

Body will essentially be a "import csv file" button, along with some other things, like a "delete current table", and a "make new table" button, maybe?
Along with this, I'd like to add a "change column name" button, and with all of this, I need to figure out how I'm going to efficiently store this stuff.
I'd like to add a search page, where you can search for a constantly updating vaue (JS) in a certain column. I'd also like to have presets, so you can
automatically sort stuff, if you have, say, a sports team, and you want to see who scored the highest (mentioned in Overview). Definitely using Jinja for
some of, if not all, of this stuff.

Footer is just going to be blank, or maybe even non-existent for now.

#### Current TODO: (Constantly Updated)
Fix visual error w/ multiple files on index DONE
CSS on /upload_file DONE
Backend on /upload_file (If a duplicate file exists, just the new file something like filename(1)) DONE
Minor CSS on /search_file DONE

Constantly updating list of items with JS on /search_file
-Get values from CSV files DONE
-Find the code for a constantly updating search return field DONE
-Figure out what to return based on different kinds of requests; need to pass in "columns" and "files" every time (I think at least) DONE
-Update the list if any values are changed, as long as the 2 dropdown fields are full DONE
-Figure out why I don't get the full CSV file returned with bigger files DONE

Work on compatibility for mobile/smaller devices

## After (Outline/Documentation)

#### Overview
This project is a flask web-app that allows you to manage CSV files, by viewing them, searching the entire file, or searching by column. It uses HTML, CSS, Jinja2, Javascript, Python, and SQLite3 to operate. Next, let's look at what each file does.

#### Templates:

apology.html: Used in Lecture 9, renders an apology page when the user inputs something incorrectly

file_update.html: Used to update the "columns" dropdown on search.html

index.html: Lists off all the files that you have saved, and adds a link to each one, so you can view the entire file inside of the webapp

layout.html: The "body" of the website. i.e., the navbar, formatting, all of that fancy stuff. We can use Jinja2 to add a block body, so we don't have to copy and paste this across all of our files

login.html: Just the login page. Slightly altered from Lecture 9

register.html: Similar to the login page. Slightly altered aswell

search.html: The main search page. Almost all of the Javascript is used here, and you can search for anything in any of your uploaded csv files

searched.html: This is what I use render the search results. This way, you don't have to re-render (is that a word?) the entirety of search.html

upload_file.html: Just allows you to upload a file, and only accepts CSV format

uploaded_files.html: Renders a file of your choice as a table; might be a little bit poorly named

#### Everything else:
styles.css: Not heavily used, just there for a few little things

app.py: Contains all of the backend routes/code for the web-app. Every "route" is described in the templates section in here (that being the README file)

final_project.db: The database; see schema.sql for more information

README.md: Hello there!

schema.sql: The schema for the database, not super fancy.