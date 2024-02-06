# Project 1

ENGO 551

The project allows users to search for books in a database and see additional information and user reviews on each of those books. The project allows users to register to the website and make their own reviews and see their reviews and books on their user profile. This is handled through the application.py file with flask. The backend databases are set up with PostgreSQL

In the application.py the routing of the pages and handling of the database is performed. 

In the import.py Only the table containing the book database is created, the other tables in the database are made directly in pgadmin4. The queries that were used can be seen in the "Project1Query" file.

The styling for the website is done in the style.scss file.

The index.html page contains the main page and search functionality. 

The login.html page allows users to login.

The register.html page allows users to register to the library app.

The bookShow.html page shows the details of a book and its reviews when the users selects a book from their search.

The user.html page allows users to see their existing reviews on books.