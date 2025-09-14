import tkinter as tk
from tkinter import ttk
import feedparser
import webbrowser
import difflib
import string

RSS_FEED = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
REFRESH_INTERVAL = 30  # seconds

def normalize(text):
    return text.lower().translate(str.maketrans("", "", string.punctuation))

def deduplicate(headlines):
    unique = []
    for h in headlines:
        norm = normalize(h[0])
        if not any(difflib.SequenceMatcher(None, norm, normalize(u[0])).ratio() > 0.75 for u in unique):
            unique.append(h)
    return unique

def categorize_headline(title):
    t = title.lower()
    death_keywords = [
        "death", "deaths", "dead", "dies", "died", "dying",
        "kill", "kills", "killed", "killing", "killings",
        "murder", "murders", "murdered", "murdering",
        "slain", "slaying", "slayings",
        "assassinate", "assassinates", "assassinated", "assassinating",
        "assassination", "assassinations", "assassin", "assassins",
        "shot", "shoot", "shoots", "shooting", "shootings", "shooter", "shooters",
        "stab", "stabs", "stabbed", "stabbing", "stabbings",
        "bomb", "bombs", "bombed", "bombing", "bombings",
        "rape", "rapes", "raped", "raping", "rapist", "rapists",
        "sniper", "snipers", "sniped", "sniping",
        "manhunt", "manhunts",
        "casualty", "casualties",
        "killer", "killers"
    ]
    death_exclusions = ["deadline", "deadly"]

    politics_keywords = [
        "election", "elections", "electoral", "electorate", "electorates",
        "elect", "elects", "elected", "electing",
        "president", "presidents", "presidency", "presidential",
        "rally", "rallies", "activist", "activists", "activism",
        "senate", "senator", "senators",
        "congress", "congressional", "congressman", "congresswoman", "congresspeople",
        "politic", "politics", "political", "politician", "politicians", "politically",
        "government", "governments", "governing", "governed",
        "parliament", "parliaments", "parliamentary", "parliamentarian",
        "policy", "policies", "policymaker", "policymakers", "policy-making",
        "campaign", "campaigns", "campaigned", "campaigning",
        "vote", "votes", "voting", "voter", "voters",
        "ballot", "ballots", "balloting",
        "republican", "republicans", "gop",
        "democrat", "democrats", "democratic",
        "white house", "administration", "administrations",
        "lawmaker", "lawmakers",
        "immigration", "immigrant", "immigrants",
        "minister", "ministers", "ministry", "ministries",
        "prime minister", "prime ministers",
        "chancellor", "chancellors",
        "diplomat", "diplomats", "diplomatic", "diplomacy",
        "legislation", "legislations", "legislature", "legislatures",
        "legislative", "legislated", "legislating",
        "law", "laws", "legal", "lawful", "unlawful",
        "governor", "governors",
        "mayor", "mayors",
        "cabinet", "cabinets",
        "conservative", "conservatives",
        "liberal", "liberals",
        "candidate", "candidates", "candidacy",
        "referendum", "referendums", "referenda",
        "coalition", "coalitions",
        "dictator", "dictators", "dictatorship", "dictatorships",
        "autocrat", "autocrats", "autocracy", "autocratic",
        "regime", "regimes",
        "monarchy", "monarch", "monarchs", "monarchies",
        "supreme court", "justice", "justices", "judiciary", "judicial",
        "impeach", "impeaches", "impeached", "impeaching", "impeachment",
        "deport", "deporting", "deportation", "deportee", "deports",
        "trade"
    ]

    politician_last_names = [
        "biden", "vance", "trump", "harris", "pelosi", "mcconnell", "mccarthy",
        "yellen", "obama", "clinton", "sanders", "warren", "deblasio",
        "bernie", "gillibrand", "alexandria", "ocasio", "gaetz", "cruz",
        "lee", "buttigieg", "pence", "bloomberg", "musk", "johnson", "kamala", "netanyahu"
    ]

    war_keywords = [
        "war", "wars", "wartime", "warfare", "warring",
        "battle", "battles", "battled", "battling", "battlefield", "battleground",
        "invade", "invades", "invaded", "invading", "invasion", "invasions",
        "conflict", "conflicts", "conflicted", "conflicting",
        "military", "militaries", "militarized", "militarization",
        "airstrike", "airstrikes", "air strike", "air strikes",
        "artillery", "missile", "missiles",
        "drone", "drones",
        "army", "armies", "navy", "navies",
        "force", "forces", "armed forces",
        "troop", "troops", "soldier", "soldiers",
        "nuclear", "bombard", "bombarded", "bombarding", "bombardment",
        "frontline", "frontlines",
        "combat", "combats", "combated", "combating", "combatant", "combatants",
        "clash", "clashes", "clashed", "clashing",
        "guerrilla", "guerrillas",
        "resistance", "occupy", "occupies", "occupied", "occupying", "occupation",
        "armed", "mercenary", "mercenaries",
        "fighter jet", "fighter jets", "air defense",
        "mobilize", "mobilizes", "mobilized", "mobilizing", "mobilization",
        "insurgent", "insurgents", "insurgency",
        "rebel", "rebels", "rebellion", "rebellions",
        "terror cell", "terror cells", "terrorist", "terrorists", "terrorism", "terroristic",
        "militant", "militants",
        "air raid", "air raids",
        "shell", "shells", "shelled", "shelling",
        "siege", "sieges", "besieged", "besieging",
        "warlord", "warlords",
        "truce", "truces",
        "ceasefire", "ceasefires",
        "hostility", "hostilities",
        "offensive", "counteroffensive", "counter-offensive",
        "weapon", "weapons", "arsenal",
        "strike", "strikes", "striking", "struck",
        "rocket", "rockets",
        "explosive", "explosives", "detonation", "detonations",
        "idf", "israeli defense force", "israeli defence force"
    ]

    if any(word in t for word in death_keywords) and not any(ex in t for ex in death_exclusions):
        return "death_headline"
    if any(word in t for word in politician_last_names) or any(word in t for word in politics_keywords):
        return "politics_headline"
    if any(word in t for word in war_keywords):
        return "war_headline"
    return "headline"

def detect_bias(title, link=""):
    text = (title + " " + link).lower()

    left_outlets = [
        "cnn.com", "cnn", "cable news network",
        "msnbc.com", "msnbc",
        "huffpost", "huffington post", "huffingtonpost.com",
        "vox.com", "vox",
        "motherjones.com", "mother jones",
        "theguardian.com", "guardian", "the guardian",
        "thedailybeast.com", "daily beast",
        "slate.com", "slate",
        "nytimes.com", "nyt", "new york times",
        "washingtonpost.com", "washington post", "wapo",
        "npr.org", "npr", "national public radio",
        "politico.com", "politico",
        "buzzfeednews.com", "buzzfeed news", "buzzfeed",
        "propublica.org", "propublica",
        "latimes.com", "los angeles times",
        "thenation.com", "the nation",
        "newrepublic.com", "new republic",
        "thinkprogress.org", "thinkprogress",
        "salon.com", "salon",
        "democracynow.org", "democracy now",
        "aljazeera.com", "al jazeera",
        "theintercept.com", "the intercept",
        "theatlantic.com", "the atlantic",
        "jacobinmag.com", "jacobin",
        "truthout.org", "truthout",
        "dailykos.com", "daily kos",
        "alternet.org", "alternet",
        "independent.co.uk", "independent",
        "newstatesman.com", "new statesman",
        "spiegel.de", "der spiegel", "spiegel",
        "lemonde.fr", "le monde",
        "liberation.fr", "liberation",
        "haaretz.com", "haaretz",
        "elpais.com", "el pais",
        "larepublica.pe", "la republica",
        "taz.de", "taz"
    ]

    right_outlets = [
        "foxnews.com", "fox news", "fox",
        "breitbart.com", "breitbart",
        "newsmax.com", "newsmax",
        "oann.com", "oann", "one america news",
        "dailywire.com", "daily wire",
        "theblaze.com", "the blaze", "blaze",
        "nationalreview.com", "national review",
        "washingtonexaminer.com", "washington examiner",
        "americanthinker.com", "american thinker",
        "thegatewaypundit.com", "gateway pundit",
        "townhall.com", "townhall",
        "pjmedia.com", "pj media",
        "nypost.com", "new york post", "nypost",
        "washingtontimes.com", "washington times",
        "thefederalist.com", "federalist",
        "dailymail.co.uk", "daily mail",
        "thesun.co.uk", "the sun",
        "telegraph.co.uk", "telegraph", "the telegraph",
        "spectator.co.uk", "the spectator", "spectator",
        "redstate.com", "red state",
        "hotair.com", "hot air",
        "dailycaller.com", "daily caller",
        "express.co.uk", "daily express", "express",
        "timesofisrael.com", "times of israel",
        "jerusalempost.com", "jerusalem post", "jpost",
        "ilgiornale.it", "il giornale",
        "theaustralian.com.au", "the australian",
        "nzherald.co.nz", "new zealand herald",
        "nation.africa", "nation", "daily nation",
        "hindustantimes.com", "hindustan times",
        "timesofindia.indiatimes.com", "times of india", "toi"
    ]

    centrist_outlets = [
        "reuters.com", "reuters",
        "apnews.com", "ap news", "associated press", "ap.org", "ap",
        "bbc.com", "bbc", "british broadcasting corporation",
        "bloomberg.com", "bloomberg",
        "wsj.com", "wsj", "wall street journal",
        "ft.com", "financial times", "ft",
        "economist.com", "the economist", "economist",
        "usatoday.com", "usa today",
        "time.com", "time magazine", "time",
        "newsweek.com", "newsweek",
        "axios.com", "axios",
        "forbes.com", "forbes",
        "marketwatch.com", "marketwatch",
        "cnbc.com", "cnbc",
        "insider.com", "business insider", "insider",
        "abcnews.go.com", "abc news", "abc",
        "cbsnews.com", "cbs news", "cbs",
        "nbcnews.com", "nbc news", "nbc",
        "pbs.org", "pbs", "public broadcasting service",
        "realclearpolitics.com", "real clear politics",
        "thehill.com", "the hill",
        "publicintegrity.org", "center for public integrity",
        "factcheck.org", "fact check",
        "snopes.com", "snopes",
        "thetimes.co.uk", "the times",
        "dw.com", "deutsche welle",
        "euronews.com", "euronews",
        "cbc.ca", "cbc", "canadian broadcasting corporation",
        "ctvnews.ca", "ctv", "ctv news",
        "globalnews.ca", "global news",
        "abc.net.au", "abc australia", "australian broadcasting corporation",
        "smh.com.au", "sydney morning herald", "smh",
        "japantimes.co.jp", "japan times",
        "straitstimes.com", "straits times",
        "scmp.com", "south china morning post", "scmp"
    ]

    if any(outlet in text for outlet in left_outlets):
        return "Left Wing"
    elif any(outlet in text for outlet in right_outlets):
        return "Right Wing"
    elif any(outlet in text for outlet in centrist_outlets):
        return "Centrist"
    else:
        return "Unclear"

def fetch_headlines():
    feed = feedparser.parse(RSS_FEED)
    headlines = [(entry.title, entry.link) for entry in feed.entries[:30]]
    return deduplicate(headlines)

def update_headlines():
    headlines = fetch_headlines()
    text_box.config(state=tk.NORMAL)
    text_box.delete("1.0", tk.END)
    for i, (title, link) in enumerate(headlines, start=1):
        tag = categorize_headline(title)
        text_box.insert(tk.END, f"{i}. {title}\n", tag)

        bias = detect_bias(title, link)
        link_tag = f"link_{i}"
        bias_tag = f"bias_{i}"

        # indented clickable link
        text_box.insert(tk.END, "      ")  # indent
        start = text_box.index(tk.END)
        text_box.insert(tk.END, "Link", link_tag)
        end = text_box.index(tk.END)
        text_box.tag_add(link_tag, start, end)
        text_box.tag_config(link_tag, foreground="#00FFFF", underline=True, font=("Consolas",8))
        text_box.tag_bind(link_tag, "<Button-1>", lambda e, url=link: webbrowser.open(url))

        # non-clickable bias text
        text_box.insert(tk.END, f" | Bias: {bias}\n\n", bias_tag)
        text_box.tag_config(bias_tag, foreground="#00FFFF", font=("Consolas",8,"italic"))

    text_box.config(state=tk.DISABLED)
    start_countdown(REFRESH_INTERVAL)

def start_countdown(seconds):
    countdown_label.config(text=f"⏳ Refreshing in {seconds} sec...")
    if seconds > 0:
        root.after(1000, start_countdown, seconds-1)
    else:
        update_headlines()

# Function to update darkness
def set_darkness(value):
    val = int(value)
    hex_color = f"#{val:02x}{val:02x}{val:02x}"
    fg_color = "#E0E0E0" if val < 200 else "#000000"
    
    root.configure(bg=hex_color)
    title_bar.configure(bg=hex_color)
    title_label.configure(bg=hex_color)
    close_btn.configure(bg=hex_color)
    legend_frame.configure(bg=hex_color)
    countdown_label.configure(bg=hex_color)
    frame.configure(bg=hex_color)
    text_box.configure(bg=hex_color, fg=fg_color)
    resize_handle.configure(bg=hex_color)
    
    for widget in legend_frame.winfo_children():
        widget.configure(bg=hex_color)
    
    # Adjust slider color to match
    darkness_slider.configure(bg=hex_color, troughcolor=hex_color, highlightbackground=hex_color)

# GUI setup
root = tk.Tk()
root.overrideredirect(True)
root.geometry("900x700")
bg_color = "black"
root.configure(bg=bg_color)

# Custom scrollbar style
style = ttk.Style(root)
style.theme_use('clam')
style.configure("Dark.Vertical.TScrollbar",
                troughcolor="#111111",
                background="#333333",
                arrowcolor="#00FFFF",
                bordercolor="#111111",
                lightcolor="#111111",
                darkcolor="#111111")

# Title bar
title_bar = tk.Frame(root, bg=bg_color, height=30)
title_bar.pack(fill=tk.X, side=tk.TOP)
title_label = tk.Label(title_bar, text="🔥 Trending News Monitor", bg=bg_color, fg="white", font=("Bahnschrift Light",12))
title_label.pack(side=tk.LEFT, padx=10)

def start_move(event):
    root.x = event.x
    root.y = event.y
def stop_move(event):
    root.x = None
    root.y = None
def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", do_move)
title_label.bind("<ButtonPress-1>", start_move)
title_label.bind("<B1-Motion>", do_move)

close_btn = tk.Button(title_bar, text="✖", bg=bg_color, fg="red", bd=0, font=("Bahnschrift Light",12), command=root.destroy)
close_btn.pack(side=tk.RIGHT, padx=5)

# Legend
legend_frame = tk.Frame(root, bg=bg_color, pady=5)
legend_frame.pack()
tk.Label(legend_frame, text="🔴 Death", fg="#FF4C4C", bg=bg_color, font=("Bahnschrift Light",12)).pack(side=tk.LEFT,padx=10)
tk.Label(legend_frame, text="🟡 Politics", fg="#FFD700", bg=bg_color, font=("Bahnschrift Light",12)).pack(side=tk.LEFT,padx=10)
tk.Label(legend_frame, text="🟢 War", fg="#00FF7F", bg=bg_color, font=("Bahnschrift Light",12)).pack(side=tk.LEFT,padx=10)
tk.Label(legend_frame, text="⚪ Other", fg="#FFFFFF", bg=bg_color, font=("Bahnschrift Light",12)).pack(side=tk.LEFT,padx=10)

countdown_label = tk.Label(root, text="", font=("Bahnschrift Light",14), bg=bg_color, fg="#00FFFF", pady=10)
countdown_label.pack()

# Darkness slider
darkness_slider = tk.Scale(root, from_=0, to=255, orient="horizontal",
                           command=set_darkness, length=150, sliderlength=15, width=15,
                           showvalue=False, label="")
darkness_slider.set(0)
darkness_slider.pack(padx=10, pady=5)

frame = tk.Frame(root, bg=bg_color)
frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

scrollbar = ttk.Scrollbar(frame, orient="vertical", style="Dark.Vertical.TScrollbar")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_box = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Segoe UI",13),
                   bg=bg_color, fg="#E0E0E0", insertbackground="white", relief=tk.FLAT, padx=10, pady=10,
                   cursor="arrow")
text_box.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=text_box.yview)

text_box.tag_config("headline", font=("Bahnschrift Light",15), foreground="#FFFFFF", spacing3=12)
text_box.tag_config("death_headline", font=("Bahnschrift Light",15), foreground="#FF4C4C", spacing3=12)
text_box.tag_config("politics_headline", font=("Bahnschrift Light",15), foreground="#FFD700", spacing3=12)
text_box.tag_config("war_headline", font=("Bahnschrift Light",15), foreground="#00FF7F", spacing3=12)

# Resize handle
resize_handle = tk.Frame(root, bg=bg_color, cursor="size_nw_se")
resize_handle.place(relx=1.0, rely=1.0, anchor="se", width=15, height=15)
def start_resize(event):
    resize_handle.start_width = root.winfo_width()
    resize_handle.start_height = root.winfo_height()
    resize_handle.start_x = event.x_root
    resize_handle.start_y = event.y_root
def do_resize(event):
    dx = event.x_root - resize_handle.start_x
    dy = event.y_root - resize_handle.start_y
    new_width = max(400, resize_handle.start_width + dx)
    new_height = max(300, resize_handle.start_height + dy)
    root.geometry(f"{new_width}x{new_height}")
resize_handle.bind("<ButtonPress-1>", start_resize)
resize_handle.bind("<B1-Motion>", do_resize)

update_headlines()
root.mainloop()
