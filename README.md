## How to run the project

- Have docker installed on your desktop
- Download the entire GIT into a folder:

- [] [Create](https://git.ku.dk/group-42/test.git)

- Make sure enterypoint.sh is LF and not CLRF.
- Open the folder in the terminal
- Run: docker-compose up –build. This will take some time initially.
- open:

- [] [Create](http://localhost:5000/) in a browser

## How to interact with the website

The website shows you quiz questions about KU admissions and courses at
SCIENCE. It will show a question, and to reciece the answer click the button.
To get a new question click the button agian. This can be repeated indefinitly.
The website has three types of questions, all of which search in the database to
find an answer.

- General Questions:
    - Hardcoded questions about the database. Such as, what is the most and so on.

- Questions about random courses:
    - Automatically selects a random course and asks for infomation about it.

- Questions about a random program at KU.
    - Automatically selects a random program at KU and asks for infomation about it.

## How we fulfilled the requirements

Our friend Joshua Nimella made KUcourses.dk and gave us acces to the api at:

- [] [Create](https://kucourses.dk/api/index.html.),

Using this we made the SQL database
with databasefiles/initialize database.py that called the api. We had to split the
api calls in two, as to not get ratelimited. We then exported the tables from
pgadmin into csv files, which is what is in the git.
For the admissions table we used:

- [] [Create](https://www.ku.dk/studier/bachelor/statistik-og-tal/),

optagelsesstatistik-2024. We coped all the the text with control c, and then
formatted it into a csv file with some python code.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
