## Test Report:
- Overall GPA needs to be changed, or also include the GPA on a 4.0 scale. (Will make a fix to this)  
    <img width="833" height="141" alt="image" src="https://github.com/user-attachments/assets/fcff8542-f555-46aa-bb7a-7b9a5946e6d3" />  
    Changed this to this new code: 

    <img width="456" height="549" alt="image" src="https://github.com/user-attachments/assets/9281bc5b-990b-46ee-9461-742c97b2ef5e" />
    This allows GPA to be calculated on a 4.0 scale. 

- When the program is exited, it doesn’t save data from students, unless you ensure it’s saved to the students.json file. Necessary knowledge for the user.
- Also, the output will not tell the user that they entered the name wrong until after the course and grades are entered. 
- One issue with going by student **name** instead of **ID** means that if a student has the same name, it will be difficult to distinguish between the two. Using an ID system ensures that each student is **definitively** unique. Therefore, it should be noted that I've also included a grade_manager_with_IDs for the case where IDs are necessary instead of names.
- The difficulty with the **Waterfall** method is that there's no testing during implementation which makes testing at the end more complicated. Rifling through lines of code is more difficult than implementing the right code from the beginning. This application would have better benefitted from **Agile** model implementation. 
