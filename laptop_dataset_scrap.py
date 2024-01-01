#!/usr/bin/env python
# coding: utf-8

# # Importing Libraries

# In[89]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import numpy as np


# # Extracting Laptop_Dataset Using BeautifulSoup

# In[2]:


product_name = []
price = []
discounted_price = []
rating = []
no_of_rating_reviews = []
info = []
for i in range(1,42):
  url = f'https://www.flipkart.com/search?q=laptops&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&sort=relevance&page={i}'
  time.sleep(1)
  page = requests.get(url)
  soup = BeautifulSoup(page.text,'lxml')
  products = soup.find_all('div',class_="_2kHMtA")
  try:
    for product in products:
      try:
        product_name.append(product.find('div',class_ ="_4rR01T").text)
      except:
        product_name.append(None)
      try:
        price.append(product.find('div',class_="_3I9_wc _27UcVY").text)
      except:
        price.append(None)
      try:
        discounted_price.append(product.find('div',class_="_30jeq3 _1_WHN1").text)
      except:
        discounted_price.append(None)
      try:
        rating.append(product.find('div',class_ ="_3LWZlK").text)
      except:
        rating.append(None)
      try:
        no_of_rating_reviews.append(product.find('span',class_="_2_R_DZ").text)
      except:
        no_of_rating_reviews.append(None)
      details = product.find('ul',class_="_1xgFaf")
      row = details.find_all('li',class_="rgWa7D")
      info.append([j.text for j in row])
  except:
    pass


# # Making pandas DataFrame

# In[3]:


df = pd.DataFrame({'product_name':product_name,'discounted_price':discounted_price,'price':price,'rating':rating,'no_of_rating_reviews':no_of_rating_reviews,'details':info})


# # Explore Dataset

# In[4]:


df.head()


# In[5]:


df.shape


# In[6]:


df.sample()


# In[7]:


df.dtypes


# In[8]:


df.info()


# # Data Wrangling

# In[9]:


# Number of duplicated columnns based on product_name,price,discounted_price,rating and no_of_rating_reviews
df[['product_name','price','discounted_price','rating','no_of_rating_reviews']].duplicated().sum()


# In[10]:


# Removing Duplicated Columns
df.drop_duplicates(subset = ['product_name','price','discounted_price','rating','no_of_rating_reviews'],inplace = True)


# In[11]:


# info after removing duplicated entities
df.info()


# In[12]:


df.shape


# In[13]:


# Removing laptops with null values in rating
df.dropna(subset = ['rating','price'],inplace = True)


# In[14]:


df.info()


# In[15]:


# Rename column names
df.rename(columns = {'product_name':'Name','discounted_price':'Selling Price','price':'MRP','rating':'Rating','details':'Details'},inplace = True)


# In[16]:


# Extracting brand name from column name 
def extr(x):
    x = x.split()
    return x[0]
# Making new column Brand
df['Brand'] = df['Name'].apply(extr)


# In[17]:


# Reshuffling columns
df = df.iloc[:,[0,6,1,2,3,4,5]]


# In[18]:


# Removing rupee sign from price columns 
def cha(x):
    x = x[1:]
    return x
df['Selling Price'] = df['Selling Price'].apply(cha)
df['MRP'] = df['MRP'].apply(cha)


# In[19]:


# changing string columns to numeric using appropriate logic
df['Selling Price'] = pd.to_numeric(df['Selling Price'].apply(lambda x:x.replace(',','')))
df['MRP'] = pd.to_numeric(df['MRP'].apply(lambda x:x.replace(',','')))
df['Rating'] = pd.to_numeric(df['Rating'])
    


# In[20]:


df.info()


# # Visualization

# In[23]:


# These many unique Brands
df['Brand'].nunique()


# In[24]:


df['Brand'].value_counts()
# Hp has highest number of laptops


# In[42]:


plt.figure(figsize = (20,12))
plt.bar(df['Brand'].value_counts().keys(),df['Brand'].value_counts(),color=['red','green','yellow','blue','orange']);
plt.title('Laptops brand on Flipkart')
plt.xlabel('Brand')
plt.ylabel('Numer of products');


# In[47]:


# same graph using plotly
x = df['Brand'].value_counts().index
y = df['Brand'].value_counts().values
df1 = pd.DataFrame({'Brand':x,'No':y})
fig = px.bar(df1,x = 'Brand',y = 'No',color = 'Brand',title = 'Brand vs No. of Laptops')
fig.show()


# In[51]:


# How many laptops with rating greater than 4
(df['Rating'] >= 4).sum()


# In[53]:


# display laptops with ratings more than 4 sorted with highest rating on top
df[df['Rating'] >= 4].sort_values('Rating',ascending = False)


# In[62]:


def det(x):
    x = str(x)
    return x


# In[63]:


df['Details'] = df['Details'].apply(det)


# In[68]:


# 369 laptops with 8 gb in its features
df['Details'].str.contains('8 GB').sum()


# In[67]:



df[df['Details'].str.contains('8 GB')]


# In[69]:


#Laptops with 8 GB and Core i7
df[df['Details'].str.contains('Core i7') & df['Details'].str.contains('8 GB')]


# In[77]:


def get_rating(x):
    y = x.replace(',','')
    return int(y.split(' ')[0])


# In[78]:


df['No_of_ratings'] = df['no_of_rating_reviews'].apply(get_rating)


# In[82]:


#laptops with more than 250 ratings and Ratings more than 4
df[(df['No_of_ratings']>250) & (df['Rating']>4)]


# In[85]:


df['Selling Price'].max()


# In[87]:


#laptop price below 50k
df[df['Selling Price'].between(0, 50000)]


# In[91]:


bins = [-np.inf,50000, 100000, 150000, 200000, np.inf]
labels = ["uptil_50k","bet_50_1L","bet_1L_1.5L","bet_1.5L_2L","abv_2L"]
df['Price_grp'] = pd.cut(df['Selling Price'], bins=bins, labels=labels)


# In[92]:


df


# In[94]:


df['Price_grp'].value_counts()


# In[95]:


plt.figure(figsize=(10,10))
plt.title('Laptop Price range on Flipkart')
plt.bar(df['Price_grp'].value_counts().keys(),df['Price_grp'].value_counts(),color=['red','green','yellow','blue','brown'])
plt.show()


# In[97]:


x1 = df['Price_grp'].value_counts().index
y1 = df['Price_grp'].value_counts().values

df2 = pd.DataFrame({'Price Group':x1,
                  'Number of Laptops':y1 })

fig = px.bar(df2, 
             x='Price Group', 
             y='Number of Laptops',
             color='Price Group', #color represents brand
             title='Price Groups of Laptops'
            )
fig.show()


# In[99]:


# laptops with sellling price greater than 2l
(df[df['Price_grp']=='abv_2L']).sort_values('Selling Price', ascending=False).head(5)


# In[100]:


df.groupby("Brand")["Selling Price"].max()


# In[103]:


#Most expensive laptops of each brand
x2 = df.groupby("Brand")["Selling Price"].max().index
y2 = df.groupby("Brand")["Selling Price"].max().values

df3 = pd.DataFrame({'Brands':x2,
                  'Costliest Laptop':y2 })

fig = px.bar(df3, 
             x='Brands', 
             y='Costliest Laptop',
             color='Brands', #color represents brand
             title='Costliest Laptop of Each Brand'
            )
fig.show()


# In[105]:


df.groupby("Brand")["Selling Price"].min()


# In[106]:


#Cheapest laptops of each brand
x3 = df.groupby("Brand")["Selling Price"].min().index
y3 = df.groupby("Brand")["Selling Price"].min().values

df4 = pd.DataFrame({'Brands':x3,
                  'Cheapest Laptop':y3 })

fig = px.bar(df4, 
             x='Brands', 
             y='Cheapest Laptop',
             color='Brands', #color represents brand
             title='Cheapest Laptop of Each Brand'
            )
fig.show()


# In[ ]:




