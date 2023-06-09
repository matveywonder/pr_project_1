#!/usr/bin/env python
# coding: utf-8

# ## Обзор данных

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as st


# In[2]:


games = pd.read_csv('/datasets/games.csv')
games.head(10)


# In[3]:


games.info()


# In[4]:


pd.DataFrame(round(games.isna().mean()*100,)
            ).style.background_gradient('coolwarm')


# Из обзора данных видно, что необходимо привести столбцы к нижнему регистру, для более читаемого вида. Изменить тип данных в столбцах: год релиза и оценки пользователей. Изучить и устранить пропущенные значения в стобцах: названия, года релиза, жанра, оценки критиков, оценки пользователей, возрастного рейтинга, если это необходимо. 

# ## Предобработка данных

# In[5]:


games.columns = games.columns.str.lower()


# In[6]:


games['name'].duplicated().sum()


# In[7]:


games = games.dropna(subset=['year_of_release'])
games = games.dropna(subset=['name'])
games = games.dropna(subset=['genre'])
#Удаляем пропуски 


# In[8]:


games['user_score'].unique()


# In[9]:


games = games.replace('tbd', np.nan)


# In[10]:


games['year_of_release'] = games['year_of_release'].astype(int)
#Меняем тип данных на целое число.
games['user_score'] = games['user_score'].astype(float)


# In[11]:


games['sum_sales'] =  games[['na_sales','eu_sales','jp_sales', 'other_sales']].sum(axis = 1)


# In[12]:


games['rating'] = games['rating'].fillna('неизвестно')


# In[13]:


games['user_score'] = games['user_score'].astype(float)
games['critic_score'] = games['critic_score'].astype(float)


# In[14]:


games.info()


# Столбцы были приведены к нижнему регистру.
# 
# В столбцах: оценка критиков и оценка пользователей, пропусков большое количество, их нельзя удалить, или заполнить, поскольку это может исказить анализ данных. Причиной пропусков может быть, отсутствие значений. Это могут быть неизвестные, неоцененные игры или недавно вышедшие. В оценке пользователей помимо обычных пропусков, были обнаружены значения 'tbd'. Их приравляли к пропускам, поскольку это неизвестное значение.
# 
# Пропуски в возрастном рейтинге, также нельзя заполнить точно, но возможно заполнить их значением 'неизвестно'.
# 
# Пропуски в столбцах с названием, годом выпуска и жанром, скорее всего связаны с тем, что у игры нет точных данных об этих характеристиках, либо разработчики забыли указать их. У нас нет данных для заполнения этих ячеек и их количество менее 2%, они не повлияют на дальнейший ход исследования, поэтому удаляем.
# 
# Имеются дубликаты в столбце с названием, но это связано с тем, что одна и таже игра выходит на разных платформах.
# 

# ## Проведение иследовательского анализа данных об играх

# In[15]:


games['year_of_release'].hist(bins=37);


# Данные по выпуску игр сильно отличаются, поэтому для нашего прогноза возьмем данные за последние 2 полных года. До 2000 года совсем не значемы, а все остальные после не достаточны актуальны для иследования и могут испортить анализ. 

# In[16]:


games.pivot_table(index='platform', values='sum_sales',
                  aggfunc='sum').sort_values(by='sum_sales', ascending=False)


# In[17]:


games.pivot_table(index='year_of_release', columns = 'platform', values='sum_sales',
                  aggfunc='sum').plot(grid=True, figsize=(16, 8), title = 'продажы всех платформ')
plt.xlabel('год')
plt.ylabel('продажи')


# Из последней сводной таблицы и графика мы можем заметить, что наиболее продаваемые платформы за все время не помогут нам в иследовании. Необходимо выделить самые популярные платформы именно за последние года.

# In[18]:


games = games.query('year_of_release >= 2014')
#делаем срез по таблице с нужными годами


# In[19]:


top_platforms = games.pivot_table(index='platform', values='sum_sales',
                  aggfunc='sum').sort_values(by='sum_sales',ascending=False)
top_platforms


# In[20]:


pl = ['PS4', 'XOne', '3DS', 'WiiU', 'PS3', 'PC', 'X360']
#составляем список из самых продаваемых платформ
games = games.query('@pl == platform')
#делаем срез по таблице с нужными платформами


# In[21]:


games.pivot_table(index='year_of_release', columns = 'platform', values='sum_sales',
                  aggfunc='sum').plot(grid=True, figsize=(16, 8), title = 'продажы популярных платформ за 2015-2016г.')
plt.xlabel('год')
plt.ylabel('продажи')
plt.show()


# Если учитывать, что данные в таблице за 2016 год неполные, в последние годы продажи расли у PS4 и XOne, у всех остальных  платформ падают продажи. Особенно сильно у приставок прошлого покаления PS3 и X360.

# In[22]:


sns.boxplot(x='platform', y='sum_sales', data=games, showfliers = False)
plt.show()


# In[23]:


sns.boxplot(x='platform', y='sum_sales', data=games)
plt.show()


# Можем наблюдать продажи платформ без выбросов и с ними. Самыми продаваемыми платформами являются PS4, XOne и WiiU. Выбросами в данном случае могут быть аномально успешные проекты. В нашем случае выбросы практически не влияют на общую картину данных.

# In[24]:


games_ps = games.query('platform == "PS4"')

influence_ps = games_ps[['critic_score', 'user_score', 'sum_sales']]
pd.plotting.scatter_matrix(influence_ps, figsize=(12, 12)) 
plt.show()
games_ps[['critic_score', 'user_score', 'sum_sales']].corr()['sum_sales']


# Можем заметить, что отзывы критиков влияют на продажи PS4, а отзывы пользователей нет.

# In[25]:


games_xone = games.query('platform == "XOne"')

influence_xone = games_xone[['critic_score', 'user_score', 'sum_sales']]
pd.plotting.scatter_matrix(influence_xone, figsize=(12, 12)) 
plt.show()
games_xone[['critic_score', 'user_score', 'sum_sales']].corr()['sum_sales']


# Такая же ситуация с XOne.

# In[26]:


games_ds = games.query('platform == "WiiU"')

influence_ds = games_ds[['critic_score', 'user_score', 'sum_sales']]
pd.plotting.scatter_matrix(influence_xone, figsize=(12, 12)) 
plt.show()
games_ds[['critic_score', 'user_score', 'sum_sales']].corr()['sum_sales']


# Для WiiU оценки пользователи влияют на продажи даже больше, чем критики.

# In[27]:


games_pc = games.query('platform == "PC"')

influence_pc = games_pc[['critic_score', 'user_score', 'sum_sales']]
pd.plotting.scatter_matrix(influence_xone, figsize=(12, 12)) 
plt.show()
games_pc[['critic_score', 'user_score', 'sum_sales']].corr()['sum_sales']


# Для PC и оценки критиков и пользователей, не сильно влияют на продажи.

# In[28]:


games.pivot_table(index='genre', values='sum_sales', aggfunc=['count','sum','mean'])


# Из построенного графика, можем заметить, что количество выпущеных игр в разные годы заметно отличается. Наиболее продаваемые платформы за все время не помогут нам в иследовании. Необходимо выделить самые популярные платформы именно за последние года. Поскольку нам необходимо составить прогноз на следующий год, возмем данные за последние два полных года, поскольку данные за 2016 год неполные - это 2014 - 2016 года. Они покажут нам актуальную информацию по платформам и продажам. Характерный срок для появления новых платформ - несколько лет, а старые исчезают примерно за 10 лет. Это связано с быстрым ростом технологий в мире. 
# 
# Абсолютный лидер по сумме продаж платформа - PS4, далее идет Xone и 3DS. Средний результат у PS3 и X360. Pc замыкает список интересующих нас платформ. Из этого следует, что большей популярностью пользуются консоли. 
# 
# За  последние два года прослеживается тенденция, что продажи расли у PS4 и XOne, у всех остальных  платформ падают продажи. Особенно сильно у приставок прошлого покаления PS3 и X360. Поэтому стоит присмотреться именно к PS4 и XOne.
# 
# Отбросив выбросы, можем наблюдать, что самыми продаваемыми платформами являются PS4, XOne и WiiU. Выбросами в данном случае могут быть аномально успешные проекты. В нашем случае выбросы практически не влияют на общую картину данных.
# 
# Можем заметить, что у популярных платформ отсутствует влияние оценки пользователей, однако оценки критиков действительно влияют на продажи. Это не удивительно, поскольку частно люди сначала прислушиваются к мнению критиков, а после игра становится популярна среди пользователей. Но у платформ с меньшем количеством продаж картина меняется, поэтому более правильно прогназировать рекламную компанию будет, опираясь на определенную платформу.
# 
# Больше всего приносят денег такие жанры как: Шутеры, Экшен, Ролеплей и Спортивные. По средним продажам жанер Шутер, довольно близко к жанру Экшен, хоть и продаж в сумме у него заметно меньше. Самые высокие средние продажы у жанра Шутер. Наиболее часто встречается жанр - Экшен. Поэтому у него большие общие продажы, хотя среднее по продажам невысокое. Самые низкие показатели у Пазл игр и стратегий. Остальные распределены примерно одинаково.
# 

# ## Составление портрета пользователя

# In[29]:


regions = games.columns[4:7]
for i in range(3):
    df_i = games.groupby('platform')[regions[i]].sum().reset_index().sort_values(regions[i], ascending = False).head(5)
    df_i.plot(x = 'platform', kind = 'bar', figsize=(8,5), grid = True, title = 'топ 5 платформ', legend=None)
    plt.xlabel('платформа')
    plt.ylabel('продажи')
    plt.show()


# In[30]:



for i in range(3):
    df_i = games.groupby('genre')[regions[i]].median().reset_index().sort_values(regions[i], ascending = False).head(5)
    df_i.plot(x = 'genre', kind = 'bar', figsize=(8,5), grid = True, title = 'топ 5 жанров', legend=None)
    plt.xlabel('жанр')
    plt.ylabel('продажи')
    plt.show()


# In[31]:


rating_pivot = games.pivot_table(index='rating', values=['na_sales', 'eu_sales', 'jp_sales'], aggfunc='sum')
rating_pivot.plot(kind = 'bar', figsize=(8,5), grid = True, title = 'влияние рейтинга')
plt.xlabel('вид рейтинга')
plt.ylabel('продажи')
plt.show()


# Продажы по регионам:
# Регион Северной Америки и Европы похожи. В них преобладают платформы PS4 и XOne, однако в Европе продажи XBox меньше и присутствует весомая доля PC пользователей. В обоих основная доля игр - шутеры. 
# Япония Сильно отличается. В ней преобладают отечественные консоли. Наибольшее количество продаж у 3DS, далее по нисходящей консоли от Sony. Жанры в этом регионе предпочитают: Ролевые, Пазлы, Файтинги.
# Можно сказать, что это связано с культурной особенностью. Европа и Северная-Америка близкие по этому фактору.
# 
# Данные по возрастному рейтингу в Японии нельзя точно определить, так как в большинстве их играх не был указан рейтинг. Возможно это игры с неопределенным рейтингом. RP.
# В Европе и Северной - Америке предпочитают игры с рейтингом М, где присутствует насилие. Это связано с большой популярностью жанра Шутер и Экшен. В целом нельзя сказать, что возрастной рейтинг влияет на продажи, скорее определенные жанры и их популярность влияют на рынок.

# ## Проверка гипотез

# In[32]:


games_clean= games.dropna(subset=['user_score'])
games_clean['user_score'].isna().sum()


# In[33]:


#H_0 Средние пользовательские рейтинги платформ Xbox One и PC !=
#H_a Средние пользовательские рейтинги платформ Xbox One и PC =

platform_xbox_one = games_clean.query('platform == "XOne"')['user_score']
platform_pc = games_clean.query('platform == "PC"')['user_score']
results = st.ttest_ind(platform_xbox_one, platform_pc,equal_var=False)
alpha = 0.05
print(results.pvalue)
if results.pvalue < alpha:
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")


# In[34]:


#H_0 Средние пользовательские рейтинги жанров Action и Sports =
#H_a Средние пользовательские рейтинги жанров Action и Sports !=

user_score_action = games_clean.query('genre == "Action"')['user_score']
user_score_sports = games_clean.query('genre == "Sports"')['user_score']
results = st.ttest_ind(user_score_action, user_score_sports,equal_var=False)
alpha = 0.05
print(results.pvalue)
if results.pvalue < alpha:
    print("Отвергаем нулевую гипотезу")
else:
    print("Не получилось отвергнуть нулевую гипотезу")


# 
# В первой гипотезе значение p-value больше 0,5%, это значит, вероятность, что средние пользовательские рейтинги платформ Xbox One и PC неравны очень низкая, поэтому мы не можем отвергнуть нулевую гипотезу.
# 
# Во-второй гипотезе значение p-value намного меньше 0,5%, это значит, вероятность, что средние пользовательские рейтинги жанров Action и Sports равны очень низкая, поэтому мы можем отвергнуть нулевую гипотезу.

# ## Общий вывод

# На этапе предобработки было обнаруже большое количество пропусков.
# В столбцах оценка критиков и оценка пользователей, нельзя удалить или заполнить пропуски, поскольку это может исказить анализ данных. Причиной пропусков может быть, отсутствие значений. Это могут быть неизвестные, неоцененные игры или недавно вышедшие. В оценке пользователей помимо обычных пропусков, были обнаружены значения 'tbd'. Их приравляли к пропускам, поскольку это неизвестное значение. Пропуски в возрастном рейтинге, также нельзя заполнить точно, но можно заполнить их значением 'неизвестно'. Возможно это рейтинг RP, который и и означает неопределенный рейтинг в таблице ESRB.
# Пропуски в столбцах с названием, годом выпуска и жанром, скорее всего связаны с тем, что у игры нет точных данных об этих характеристиках, либо разработчики забыли указать их. У нас нет данных для заполнения этих ячеек и их количество менее 2%, они не повлияют на дальнейший ход исследования, поэтому данные были удалены.
# 
# Количество выпущеных игр в разные годы заметно отличается. Наиболее продаваемые платформы за все время не помогут нам в иследовании. Необходимо выделить самые популярные платформы именно за последние года. Поскольку нам необходимо составить прогноз на следующий год, возмем данные за последние два полных года, поскольку данные за 2016 год неполные - это 2014 - 2016 года. Они покажут нам актуальную информацию по платформам и продажам. Характерный срок для появления новых платформ - несколько лет, а старые исчезают примерно за 10 лет. Это связано с быстрым ростом технологий в мире. 
# 
# За  последние два года прослеживается тенденция, что продажи расли у PS4 и XOne, у всех остальных  платформ падают продажи. Особенно сильно у приставок прошлого покаления PS3 и X360. Поэтому стоит присмотреться именно к PS4 и XOne.
# 
# Абсолютный лидер по сумме продаж платформа - PS4, далее идет Xone и 3DS. Средний результат у PS3 и X360. Pc замыкает список интересующих нас платформ. Из этого следует, что большей популярностью пользуются консоли. 
# 
# 
# Отбросив выбросы, можем наблюдать, что самыми продаваемыми платформами являются PS4, XOne и WiiU. Выбросами в данном случае могут быть аномально успешные проекты. В нашем случае выбросы практически не влияют на общую картину данных.
# 
# Можем заметить, что у популярных платформ отсутствует влияние оценки пользователей, однако оценки критиков действительно влияют на продажи. Это не удивительно, поскольку частно люди сначала прислушиваются к мнению критиков, а после игра становится популярна среди пользователей. Но у платформ с меньшем количеством продаж картина меняется, поэтому более правильно прогназировать рекламную компанию будет, опираясь на определенную платформу.
# 
# Больше всего приносят денег такие жанры как: Шутеры, Экшен, Ролеплей и Спортивные. По средним продажам жанер Шутер, довольно близко к жанру Экшен, хоть и продаж в сумме у него заметно меньше. Самые высокие средние продажы у жанра Шутер. Наиболее часто встречается жанр - Экшен. Поэтому у него большие общие продажы, хотя среднее по продажам невысокое. Самые низкие показатели у Пазл игр и стратегий. Остальные распределены примерно одинаково.
# 
# 
# Возможно в последнее время стали более популярны бесплатные игры с системой внутриигровой покупки, поэтому цифры по продажам упали. Либо новые проекты находятся в стадии разработки.
# 
# В рекламной компании стоит сделать ставку на продвижение игр среди критиков, так же постараться уделить внимание тем играм у которых хорошие оценки. 
# 
# Для успешной рекламной компании, будут самыми востребоваными жанры, которые приносят больше всего денег: Шутеры, Экшен, Ролеплей и Спортивные. 
# 
# Регион Северной Америки и Европы похожи. В них преобладают платформы PS4 и XOne, однако в Европе продажи XBox меньше и присутствует весомая доля PC пользователей. В обоих основная доля игр - шутеры. 
# Япония Сильно отличается. В ней преобладают отечественные консоли. Наибольшее количество продаж у 3DS, далее по нисходящей консоли от Sony. Жанры в этом регионе предпочитают: Ролевые, Пазлы, Файтинги.
# Можно сказать, что это связано с культурной особенностью. Европа и Северная-Америка близкие по этому фактору.
# Из этого может следовать, что рекламную компанию нужно делать основываясь на регионе.
# 
# В Европе и Северной - Америке предпочитают игры с рейтингом М, где присутствует насилие. Это связано с большой популярностью жанра Шутер и Экшен. Нельзя однозначно сказать, что возрастной рейтинг влияет на продажи, скорее определенные жанры и их популярность влияют на рынок. При этом, американская система оценки возрастной категории не катируется в Японии, поэтому по этому региону мы не можем точно составить оценку.
# 
# Средние пользовательские рейтинги платформ и жанров могут отличаться, но нельзя говорить о том, что присутствует закономерность, влияющая на продажи.

# In[ ]:




