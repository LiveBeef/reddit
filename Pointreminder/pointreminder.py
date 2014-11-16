#/u/GoldenSights
import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import sqlite3

'''USER CONFIGURATION'''

USERNAME  = ""
#This is the bot's Username. In order to send mail, he must have some amount of Karma.
PASSWORD  = ""
#This is the bot's Password. 
USERAGENT = ""
#This is a short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
SUBREDDIT = "GoldTesting"
#This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
TITLETAG = "[request]"
#If this is non-blank, then this string must be in the title or flair of the post to work
TRIGGERS = ["thanks"]
#These tell the bot to make the comment
TRIGGERREQUIRED = False
#If this is True, the comment must contain a trigger to post
#If this is False, the comment will be posted as long as there are no anti-triggers
#Anti-triggers will ALWAYS deny the post.
ANTITRIGGERS = ["✓", "thanks but", "thanks, but"]
#These force the bot not to make the comment.
REPLYSTRING = "Dont forget to give a\n\n> ✓\n\n(see sidebar)!"
#This is the word you want to put in reply
MAXPOSTS = 100
#This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
WAIT = 50
#This is how many seconds you will wait between cycles. The bot is completely inactive during this time.


'''All done!'''




WAITS = str(WAIT)
try:
    import bot #This is a file in my python library which contains my Bot's username and password. I can push code to Git without showing credentials
    USERNAME = bot.uG
    PASSWORD = bot.pG
    USERAGENT = bot.aG
except ImportError:
    pass

sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded Completed table')

sql.commit()

r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD) 

def scanSub():
    print('Searching '+ SUBREDDIT + '.')
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_comments(limit=MAXPOSTS)
    for post in posts:
        pid = post.fullname
        cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
        if not cur.fetchone():
            if not post.is_root:
                print('Getting submission for ' + pid)
                submission = post.submission
                if not submission.link_flair_text:
                    submission.link_flair_text = ""
                stitle = submission.title.lower()+' '+submission.link_flair_text.lower()
                if TITLETAG == "" or TITLETAG.lower() in stitle:
                    try:
                        pauthor = post.author.name
                        sauthor = submission.author.name
                        if pauthor == sauthor:
                            if TRIGGERREQUIRED ==False or any(trig.lower() in post.body.lower() for trig in TRIGGERS):
                                if not any(atrig.lower() in post.body.lower() for atrig in ANTITRIGGERS):
                                    print('Replying to ' + pauthor + ', ' + pid)
                                    post.reply(REPLYSTRING)
                    except AttributeError:
                        print('Either commenter or OP is deleted. Skipping.')

            cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
            sql.commit()


while True:
    try:
        scanSub()
    except Exception as e:
        print('An error has occured:', e)
    print('Running again in ' + WAITS + ' seconds \n')
    sql.commit()
    time.sleep(WAIT)

    
