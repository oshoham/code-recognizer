import os, json, requests, time, shutil, sys
from subprocess import call
from getpass import getpass

def check_rate_limit(num_requests, username, password):
    rate_limit_req = requests.get('https://api.github.com/rate_limit', auth = (username, password))
    rate_limit_data = rate_limit_req.json()
    
    if 'message' in rate_limit_data:
        print 'Error communicating with GitHub: {}.'.format(rate_limit_data['message'])
        exit()

    rate_limit = rate_limit_data['resources']['search']
    remaining_requests = rate_limit['remaining']
    reset_time = int(rate_limit['reset']-time.time())

    if remaining_requests == 0:
        print 'No GitHub search requests remaining. Requests will reset in {} seconds.'.format(reset_time)
        exit()
    elif remaining_requests < num_requests:
        print 'Insufficient GitHub search requests to find code for all requested languages. Requests will reset in {} seconds.'.format(reset_time)
        exit()
    else:
        print '{} GitHub search requests remaining.'.format(remaining_requests)

# for use as a helper function to os.path.walk()
def remove_unwanted_files(args, directory, files):
    extension = args[0]
    destination_directory = args[1]
    for f in files:
        if os.path.isfile(os.path.join(directory, f)):
            if not f.endswith(extension):
                os.remove(os.path.join(directory, f))
            else:
                return_code = call(['mv', os.path.join(directory, f), destination_directory])

def get_code(languages = {'c', 'java', 'python', 'js', 'haskell'}):
    file_extensions = {'haskell':'.hs', 'java':'.java', 'c':'.c', 'js':'.js', 'python':'.py'}
    for language in languages:
        if language not in file_extensions:
            print '{} is not a recognized language.'.format(language)
            languages.remove(language)
    if len(languages) == 0:
        print 'None of the specified languages were recognized.'
        exit()

    print 'Enter your GitHub login credentials.'
    username = raw_input('username: ')
    password = getpass('password: ')

    gh_url = 'https://api.github.com'
    samples_per_language = 5

    search_string = 'https://api.github.com/search/repositories?q=language:'
    sorting_options = '&sort:stars'

    print 'Checking GitHub search API rate limit...'
    check_rate_limit(len(languages), username, password)

    code_samples_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "code_samples")
    if os.path.isdir(code_samples_directory):
        overwrite = raw_input('Code samples directory already exists. Overwrite it? (y/n) ')
        if overwrite == 'y':
            shutil.rmtree(code_samples_directory)
        else:
            exit()
    else:
        print 'Code samples directory not found. Creating directory at {}...'.format(code_samples_directory)
    os.makedirs(code_samples_directory)


    for language in languages:
        print 'Downloading git repositories containing {} code'.format(language)

        gh_query = search_string + language + sorting_options
        gh_response = requests.get(gh_query, auth = (username, password)).json()

        # make sure we're not trying to get more repositories than we have available
        repo_count = gh_response['total_count']
        if repo_count < samples_per_language:
            samples_per_language = repo_count

        repositories = gh_response['items']

        for i in xrange(samples_per_language):
            clone_url = repositories[i]['clone_url']
            name = repositories[i]['name']
            repo_dir = os.path.join(code_samples_directory, name)
            print 'Cloning repository from {}...'.format(clone_url)
            return_code = call(['git', 'clone', clone_url, repo_dir])
            
            print 'Removing unnecessary files...'

            os.path.walk(repo_dir, remove_unwanted_files, (file_extensions[language], code_samples_directory))
            shutil.rmtree(repo_dir)

        print 'Finished downloading {} repositories.'.format(language)

if __name__ == '__main__':
    languages = set([])
    if(len(sys.argv) > 1):
        for i in xrange(1, len(sys.argv)):
            languages.add(sys.argv[1])
        get_code(languages)
    else:
        get_code()
