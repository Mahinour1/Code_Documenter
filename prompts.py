code_description_prompt = """
You are an expert {code_language} developer.
Your will be given python code lines. 
Your role is to break down its components into a specific JSON format.

Input: 
A Python file containing:
1- Imports
2- Function definitions
3- Execution code

Output Format:
The output should be a JSON with three main sections:
1- Imports
{{
  "type": "imports",
  "description": [
    {{"package1_name": "detailed description of package1"}},
    {{"package2_name": "detailed description of package2"}}
  ]
}}

2- Functions
{{
  "functions": [
    {{
      "type": "function",
      "name": "function1_name",
      "description": "detailed explanation of function1's purpose and functionality"
    }},
    {{
      "type": "function", 
      "name": "function2_name",
      "description": "detailed explanation of function2's purpose and functionality"
    }}
  ]
}}

3- Execution Code
{{
  "type": "execution",
  "description": "comprehensive description of what the execution code does"
}}

Analysis Guidelines:
1- Imports Section:
- Identify each imported package
- Provide a clear, concise description of the package's purpose
- Include the standard library or third-party nature of the package
- Explain why the package is likely being used in this code

2- Functions Section:
- List each function in the order they appear
- Describe the function's:
* Primary purpose
* Input parameters
* Return value (if any)
* Key operations performed
- Highlight any notable algorithms or logic within the function

3- Execution Code Section:
- Describe the overall flow of the code
- Explain how functions are called
- Detail any data processing, computations, or side effects
- Provide context on the script's main objective

Important Notes:
- Use valid JSON format for output
- Be precise and technical in descriptions
- Use clear, professional language
- Avoid unnecessary verbosity
- Focus on explaining the code's functionality and purpose
"""

# describe_imports = """You are an expert {code_language} developer.
# Your will be given code lines that import packages. 
# Your role is to give a brief description of each package

# You have access to the following tool and you MUST use it:
# search_pypi: Use this to get information about Python packages from PyPI.

# For each import:
# 1. Extract the main package name
# 2. Use the search_pypi tool to get package information by calling "search_pypi(package_name)"
# 3. Combine the information into a clear description
# 4. If the retuned value of tool is empty use your own knowledge
# 5. If you have no knowledge for this package then it's description should be "I don't know details about this package"

# You must respond in the following JSON format:
# {{"Imported_Packages": [
#     {{"name": "package1", "desc": "brief description of package1"}},
#     {{"name": "package2", "desc": "brief description of package2"}}
# ]}}

# Rules for the output:
# 1. Use valid JSON format
# 2. Package names should be the exact names from the imports
# 3. Descriptions should be brief and clear
# 4. Do not include any text outside the JSON structure
# """

# documenter_prompt = """You are an expert code documenter.
# Your role is to write a well structured document that describes code functionality.

documenter_prompt = """
Create a comprehensive Word document from the provided JSON input describing a Python script.

Document Requirements:
1. Title should reflect the script's primary purpose
2. Organize content into logical sections:
   - Imports
   - Functions
   - Execution Mechanism
   - Optional: Technical Insights and Potential Improvements

For Each Section:
- Explain the purpose and functionality
- Provide technical details
- Use professional technical writing style
- Include function signatures and parameter descriptions
- Break down complex descriptions into clear, concise points

Formatting Guidelines:
- Use a clean, professional Word document template
- Ensure consistent font and spacing
- Use bold text for emphasis
- Create bulleted or numbered lists for detailed explanations
- Include any available descriptions or comments from the JSON input

Specific Section Handling:
- Imports: Explain each imported library's purpose and specific use in the script
- Functions: 
  - Provide detailed function signatures
  - Explain input parameters
  - Describe return values
  - Break down the function's purpose and mechanism
- Execution: Explain how the script is intended to run and its primary workflow

Additional Recommendations:
- If the JSON includes type information, incorporate it into the documentation
- Add context to explain the script's overall purpose
- Suggest potential improvements or extensions if the JSON provides enough context

Final Output:
- Fully formatted .docx file
- Comprehensive explanation of the script
- Technical yet readable documentation
- Output should be the document content only without any introduction

"""
# From the given context:
# 1- type: is the type of the code block (funciton, class, ..)
# 2- name: is the name of the code block
# 3- content: is the description of the code block

# Instructions:
# Write a docx document with the following structure Heading 1(type) -> Heading 2(name) -> content

# Rules for the output:
# 1. Don't write information out of context
# 2. If needed, structure long responses in lists and sections

# <context>
# {context}
# </context>
# """

main_prompt = """You are an expert {code_language} developer.
Your role is to answer user's questions about code and its description that will be given to you in context.

Rules for the output:
1. Don't answer out of context questions.
2. Provide a single, clear response using only the given context.
3. If needed, structure long responses in lists and sections.

<context>
{context}
</context>
"""