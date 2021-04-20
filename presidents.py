import requests

def parse_election_line(line):
    if line.startswith(("turnout", "needed_votes", 
                        "nominee", "party", 
                        "running_mate", "home_state", 
                        "electoral_vote", "states_carried", 
                        "popular_vote", "percentage")):
        
        line_parts = line.split("=")
        
        field_name = line_parts[0].strip()
        if field_name[-1].isdigit():
                field_name = field_name[:-1]
                
        field_val = line_parts[1]
        
        #remove common unneccessary parts of value that are common to percentage and other fields
        field_val = field_val \
                .split("<")[0] \
                .split("(")[0] \
                .split("+")[0] \
                .strip()
        
        if field_name.startswith("percentage"):
            if field_val.startswith("{{"):
                percent_line = field_val.split("|")
                nominee_votes = percent_line[1].split(":")[1].replace(",", "").strip()
                num_total_votes = percent_line[2].split(":")[1].replace(",", "").strip()
                #we'll cast this back later, but for consistently make it a string
                field_val = str(round((float(nominee_votes) / float(num_total_votes)*100), 1)) 
            else:
                field_val = field_val.split("%")[0].strip()
        else: 
            #remove unnecessary parts that are common to fields besides percentage
            field_val = field_val \
                .split("|")[0] \
                .split("{{")[0] \
                .split("%")[0] \
                .strip()
            if field_name.startswith("popular_vote"):
                field_val = field_val.replace(",", "")
            elif field_name.startswith("turnout"):
                if (field_val.find("\n") != -1):
                    field_val = field_val.split("\n")[1].strip()
        return (field_name, field_val)
    return None
  
candidate_list = []
  
def get_election_info(year):
    params = {
        "action":"parse",
        "page": str(year) + " United States presidential election",
        "prop": "wikitext",
        "section": 0,
        "format": "json",
    }
    
    url = "https://en.wikipedia.org/w/api.php"
    
    #The 1788 election continued into 1789 so its title is '1788-89 US presidential election'
    if year == 1788:
        year = str(year) + "-89"
        url += "?"
        for label, param in params.items():
            url += (label + "=" + str(param).replace(" ", "+") + "&")
        url += "redirects"
        resp = requests.get(url)
    else:
        resp = requests.get(url, params=params)
        
    data = resp.json()
    
    wikitext=data['parse']['wikitext']['*']
    start_ind = wikitext.find('Infobox election')
    end_ind = wikitext.find('map')
    wikitext = wikitext[start_ind:end_ind]
    
    #Perform preliminary replacing of characters we don't need
    wikitext = wikitext \
        .replace('[[', '') \
        .replace(']]', '') \
        .replace('\'\'\'', '') \
        .replace("<!--", "") \
        .replace("-->", "")
        
    lines = wikitext.split('\n|')
    
    #list of dictionaries
    nominees = [] #list of nominees
    nominees_dict = {} #nominee info
    nominees_dict['year'] = year
    
    for line in lines: 
        line = line.strip()
        line_contents = parse_election_line(line)
        
        if line_contents is not None:
            field_name = line_contents[0]
            field_val = line_contents[1]
            nominees_dict[field_name] = field_val
        
            if field_name == 'nominee':
                candidate_list.append(field_val)
        
            elif field_name == 'percentage':
                nominees.append(nominees_dict)
                turnout = nominees_dict['turnout']
                needed_votes = nominees_dict['needed_votes']
                nominees_dict = {}
                nominees_dict['turnout'] = turnout
                nominees_dict['needed_votes'] = needed_votes
                nominees_dict['year'] = year
    
    return nominees
  
