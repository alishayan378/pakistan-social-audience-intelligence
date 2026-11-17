import csv, random
random.seed(23)
brands=["Lahore Loom","Rang Studio","Mehr Pret"]; platforms=["Instagram","TikTok","Facebook"]
campaigns=["Eid Edit","11.11 Sale","Winter Lawn","New Arrivals"]
formats=["Reel","Product photo","Influencer post","Styling video","Sale announcement","Eid campaign"]
bank=[("Price please?","English","price"),("Is this available in Karachi?","English","availability"),("Bohat khoobsurat suit hai","Roman Urdu","praise"),("Price bohat zyada hai","Roman Urdu","price"),("Delivery kitne din mein hogi?","Roman Urdu","delivery"),("Any discount on this suit?","English","discount"),("Ordered last week, still waiting","English","delivery"),("Inbox me details send kar dein","Roman Urdu","purchase"),("Fabric ki quality kaisi hai?","Roman Urdu","quality"),("Small size available?","English","sizing"),("Please share size chart","English","sizing"),("Lawn fabric hai?","Roman Urdu","quality"),("COD available?","English","purchase"),("Is there a sale?","English","discount"),("Mujhe yeh design chahiye","Roman Urdu","purchase"),("Karachi delivery charges?","English","delivery")]
posts=[]; comments=[]
for i in range(1,181):
 pid=f"P{i:04}"; brand=random.choice(brands); platform=random.choice(platforms); campaign=random.choice(campaigns); fmt=random.choice(formats); count=max(8,int(random.lognormvariate(3.2,.55))); likes=int(count*random.uniform(5,14)); shares=int(count*random.uniform(.25,1.2)); views=int(likes*random.uniform(8,24))
 if i in (17,82,149): likes*=5; shares*=4; views*=2
 if i in (39,121): views*=4; likes=max(5,likes//2)
 posts.append([pid,brand,platform,campaign,fmt,"Women's lawn suit",likes,count,shares,views,random.randint(1,30)])
 theme=random.choice(["price","price","quality","sizing","delivery","discount","availability","purchase","praise"])
 for _ in range(count):
  pool=[x for x in bank if x[2]==theme] if random.random()<.48 else bank; msg,lang,_=random.choice(pool); comments.append([pid,msg,lang])
with open('data/demo_posts.csv','w',newline='',encoding='utf-8') as f:
 w=csv.writer(f); w.writerow(['post_id','brand','platform','campaign','content_type','product_category','likes','comments_count','shares','views','days_since_post']); w.writerows(posts)
with open('data/demo_comments.csv','w',newline='',encoding='utf-8') as f:
 w=csv.writer(f); w.writerow(['post_id','comment_text','language_type']); w.writerows(comments)
print(f'Wrote {len(posts)} synthetic posts and {len(comments)} synthetic comments')
