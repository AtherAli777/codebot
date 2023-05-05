from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm 
from .forms import SignUpForm
from .models import Code
from langchain import PromptTemplate
from django.conf import settings
import openai

LANG_LIST = ['aspnet', 'c', 'clike', 'cpp', 'csharp', 'css', 'csv', 'django', 'html', 'java', 'javascript', 'markup', 'markup-templating', 'matlab', 'mongodb', 'python', 'r', 'regex', 'ruby', 'sass', 'sql', 'typescript']


def openai_api_call(api_key, prompt, lang):
    try:
        openai.api_key = api_key
        openai.Model.list()
        #This should select the correct GPT-3 engine model for the selected programming language, and generate a more accurate response.
        engine_map = {
            'aspnet': 'text-davinci-003',
            'c': 'text-davinci-003',
            'clike': 'text-davinci-003',
            'cpp': 'text-davinci-003',
            'csharp': 'text-davinci-003',
            'css': 'text-davinci-003',
            'django': 'text-davinci-003',
            'html': 'text-davinci-003',
            'java': 'text-davinci-003',
            'javascript': 'text-davinci-003',
            'markup': 'text-davinci-003',
            'markup-templating': 'text-davinci-003',
            'matlab': 'text-davinci-003',
            'mongodb': 'text-davinci-003',
            'python': 'text-davinci-003',
            'r': 'text-davinci-003',
            'regex': 'text-davinci-003',
            'ruby': 'text-davinci-003',
            'sass': 'text-davinci-003',
            'sql': 'text-davinci-003',
            'typescript': 'text-davinci-003'
        }

        # Make an OpenAI Request
        response = openai.Completion.create(
            engine=engine_map[lang],
            prompt=prompt,
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

        #parse the response 
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return str(e)



# Create your views here.
def home(request):
    if request.method == 'POST':
        coder = request.POST.get('coder', None)
        options = request.POST.get('options', None)
        api_key = request.POST.get('api_key', None)

        #if no programming language is selected
        if options == 'Select programming language':
            messages.success(request, "Please Select a programming language")
            return render(request, 'index.html', {'lang_list': LANG_LIST, 'coder': coder, 'options': options})
        
        else:
            
            template = """
            "Please only provide code and not any text. If any text is provided, don't print any output with programming syntax
            instead respond with "Please write code only".

            Code:

            Question: {query}

            Answer: 
            """
            prompt_template = PromptTemplate(
                input_variables=["query"],
                template=template
            )

            prompt = prompt_template.format(
                query=f"Write a code snippet using {options} to fix the code only:{coder}"
            )
            
            response = openai_api_call(api_key,prompt,options)   
            if not coder:
                messages.success(request, "Please provide some code")
                return render(request, 'index.html', {'lang_list': LANG_LIST, 'coder': coder, 'options': options})
 
            #save in database
            record = Code(question=coder,code_answer=response, language=options,  user=request.user)
            record.save()
            past = Code.objects.all()
            return render(request, 'index.html', {'lang_list': LANG_LIST, 'reponse': response, 'options': options, 'past': past})

    return render(request, 'index.html', {'lang_list': LANG_LIST})

def suggest(request):
    if request.method == 'POST':
        coder = request.POST.get('coder', None)
        options = request.POST.get('options', None)
        api_key = request.POST.get('api_key', None)

        # Check if a programming language has been selected
        if options == 'Select programming language':
            messages.success(request,"Please select programming language")
            return render(request, 'suggest.html', {'lang_list': LANG_LIST, 'coder': coder, 'options': options})
        else:
            # Save code in the database
            prompt = f"Respond with code only. using {options} code: {coder}"
            
            response = openai_api_call(api_key,prompt,options)
            record = Code(question=coder,code_answer=response, language=options, user=request.user)
            record.save()
            return render(request, 'suggest.html', {'lang_list': LANG_LIST, 'reponse': response})
        
    # If method is not POST, render the page with language list    
    return render(request, 'suggest.html',{'lang_list': LANG_LIST})

# Define a view for the past codes
def past(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve all past codes for the current user
        past = Code.objects.filter(user_id = request.user.id)
        # Render the past.html template with the past codes
        return render(request, 'past.html', {'past': past})
    else:
        # If the user is not authenticated, display a message and redirect to the home page
        messages.success(request,"User must be logged in")
        redirect('home')

# Define a function for user login
# Here We are not saving the form we are just authenticating the form
def login_user(request):
    if request.method == 'POST':
        # Get username and password from the POST request
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user using the provided credentials
        user = authenticate(request, username=username, password=password)
        
        # If the user is authenticated, log them in and redirect to home page
        if user is not None:
            login(request, user)
            messages.success(request,"You have successfully logged in")
            return redirect('home')
        
        # If the user is not authenticated, redirect to home page and display a message
        else:
            messages.error(request,"check your username and password")
            return redirect('home')
    
    # If the request method is not POST, render the login page
    else:
        return render(request, 'index.html',{})
    
# Define a function for user logout
def logout_user(request):
    # Log the user out and redirect to home page
    logout(request)
    messages.success(request,"You have successfully logged out")
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()   # save the user information to the database
            username = form.cleaned_data.get('username')  # get the username from the submitted form
            password = form.cleaned_data.get('password1')  # get the password from the submitted form
            user = authenticate(request=request, username=username, password=password)  # authenticate the user
            if user is not None:  # if the user exists and is authenticated
                login(request, user)  # log in the user
                messages.success(request, 'Registered successfully.')  # show a success message
                return redirect('home')  # redirect to the home page
        else:  # if the form is not valid
            messages.error(request, 'Invalid form submission.')  # show an error message
    else:  # if the request method is not POST
        form = SignUpForm()  # create a new form
    return render(request, 'register.html', {'form': form})  # render the registration page with the form



def delete(request, list_id):
    item = Code.objects.get(pk=list_id)  # get the object with the provided ID from the database
    item.delete()  # delete the object
    messages.success(request, 'Chat deleted successfully!')  # show a success message
    return redirect('past')  # redirect to the past chats page


