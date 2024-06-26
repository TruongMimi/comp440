# Documentation link: https://docs.google.com/document/d/1slflqyFsyQEF16hjyRkONlbcwcmgUcdMiprGFqYdD08/edit?usp=sharing
# Power point: https://docs.google.com/presentation/d/1FJu1dUK1uu6NG4D4IZ2k3OoIIug96sFK/edit?usp=sharing&ouid=105119885583782901381&rtpof=true&sd=true

# Project Description 

Presentation date: 5/2/2024

Project: Design and implement a publication-listing service. The service should permit entering of information about publications, such as title, authors, year, where the publication appeared, and pages. Authors should be a separate entity with attributes such as name, institution, department, email, address, and home page. Your application should support multiple views on the same data. For instance, you should provide all publications by a given author (sorted by year, for example), or all publications by authors from a given institution or department. You should also support search by keywords, on the overall database as well as within each of the views.

The Final Project will involve creating a database, with functionality based on the topic that has been approved by the instructor.
Teams will be composed of two students and they will present their database interface, along with a slide presentation describing the functions. The presentation days will be scheduled randomly, per team, by the professor.

Requirements:
  - MySQL database with appropriate tables, keys, relations, etc.
  - ER Diagram that describes your database (MySQL Workbench can help you with that)
  - User Interface (web-browser or some form of GUI) to manipulate the database (to enter, delete, modify, search the data)
  - One page paper describing your database functions in detail
  - 3-5 slide presentation, which will accompany your class demonstration

What to submit (all zipped):
  - MySQL database file and supporting interface files/application
    - Database and supporting files must be zipped and submitted to Canvas. If you prefer to implement remotely (repl.it, PHP, GitHub, etc.), you must provide the link and full access to the database file
  - ER Diagram
  - Paper
  - Slide presentation
    
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Github
- Github is an online platform that is utilized for hosting code to allow users to control the version and collaborate with other users. It also tracks the versions that got changed and which user changed them. 

  # Cloning Github
  To ensure that you have the github repository on the computer
  1) Using Windows powershell and use the following command
       - git clone https://github.com/TruongMimi/comp440

# Docker
- Docker is an online platform that is utilized for building, testing and deploying applications. It is useful for collaboration in projects.
- If there are a significant amount of changes, it is recommended to remove the container and image completely and rerun the commands to set up the image and container again. 
  # Docker Install Instructions 
  1) Click the link that corresponds with your computer.
      - Windows download
           - https://docs.docker.com/desktop/install/windows-install/
      - Mac download
           - https://docs.docker.com/desktop/install/mac-install/
             
  3) Follow the installation instructions.
  4) Using Windows powershell navigate to the path of where your cloned repository is placed.
      - example unix commands
            - CD => to change directory
            - dir => to look at the contents of the directory.
  5) Once you have navigated to the docker directory and finished setting up the docker software, create a docker image 
        
  # Building a Docker image 
  1. Ensure that the Dockerfile is on the root of the project and has commands to copy the appropriate files to locations on the Docker container. 
    - This is the repo with your relevant code for this project with the Dockerfile set up for a flask app can be found here: https://github.com/TruongMimi/comp440
    - Before building the docker image, please add your local IP address to the "host" section of dbconfig in app.py
  2. Open a terminal
  3. Within the terminal, navigate to the directory where your project is (this assumes you've cloned the GitHub repo to your computer)
  4. Enter the following command: docker build -t [IMAGE_NAME]:[IMAGE_VERSION] .
     - This is the command for our specific project. 
         - docker build -t comp440:comp440 .
     - Here is an example docker build command to use: docker build -t test:1.0 . 
  5. There will be some output on the terminal where it will be completing each step specified within the Dockerfile
     - You'll know if there are any errors because the errors are usually pretty specific

  # Creating and Running a Docker Container
  1. Open a terminal (if not already open from the previous section of building a Docker image)
  2. Within the terminal, navigate to the directory where your project is (this assumes you've cloned the GitHub repo to your computer)
  3. Enter the following command to create a network for a local mysql database to be connected to: docker network create my-network
  4. Enter the following command: docker run --name [CONTAINER_NAME] -d -p 5000:5000 --network=my-network [IMAGE_NAME]:[IMAGE_VERSION]
      - This is the command for our specific project.
          - docker run --name comp440 -d -p 5000:5000 --network=my-network comp440:comp440
      - If you don't specify a name, it just assigns it's own ridiculous naming scheme. They're too hard to type or remember.
      - You can change the ports that the container runs on. You can also have multiple running, as long as they are not on the same port (5000:5000 is used in the above command)
      - The port is also defined in app.py, so make sure to change that as well if you change the port number. You can find the example on the GitHub repo I sent in the previous section.
  5. The output will be a bunch of numbers or something like that (one line) if the creation/running of the docker container was successful
  6. Now, depending on what you've set as your homepage for the app, open a browser and put in the following URL: 127.0.0.1:5000
      - This assumes that the port is 5000 for the container to run on and that there is a page available and routing available for '/' in the URL
  7. If all is set up properly on the app side/code side, then you should see your app's page!

  # Removing Docker container and image
  1. Open the Docker Desktop application
  2. Click on the tab “Containers”
  3. Click the little trash can icon to the far right of the container that’s listed 
      - You can delete while it’s still running but, if not, just click the stop icon before clicking the trash can icon.
  4. Confirm 
  5. Click on the tab “Images”
  6. Click on the little trash can icon to the far right of the image that’s listed
  7. Confirm

# How to import the database into MySQL 
  - To enter a csv file into the database, you would go to your schema in MySQL
  - find the publication_listing
  - Expand table
  - Find publication and right click
  - select 'table data import wizard'
  - Do this for all 3 csv files in this order
        - Publication (must be first since it has the primary key and foreign keys for each table, order after this doesn't matter) 
        - Author 
        - Keywords 


# If you want to see example data Loading CSV files onto the database 
     Order of CSV uploads 
       1. Publication // since it has the foreign key for the other tables 
       2. Then any file is fine after 

# Running locally 
   - Locate to the path that you run the following code in the windows powershell
        - python app.py
   - open the brower and put in your IP address
        - http://127.0.0.1:5000/
# User sign up 
   - Needs First name, Last Name, address, and Email (error handling @), Password is required (must be more than 6 characters)

# Add Publication 
    - Needed for adding a publiation 
       - Title 
       - Date Published 
       - Pages
       - DOI
       - Link 
       
# Search Pulication 
    - Can search by the following values 
       - Title 
       - Author
       - Year 
       - Link 
       - Pages
       - Keywords
       
# Delete Publication 
    - Search for the specific publication
    - Click the title of the publication
    - Confirm deletion
    - Delete publication


# Modify Publication 
    - Search for the specific publication you want to modify 
    - Click the title of the publication you want to modify 
    - Change what you want 
    - Submit










