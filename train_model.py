import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle


df = pd.read_csv('PATH', delimiter='\t')
df.columns = df.columns.str.strip()

df['ascites'] = df['ascites'].map({'Yes':1, 'No':0})
df['hepatomegaly'] = df['hepatomegaly'].map({'Yes':1, 'No':0})
df['spiders'] = df['spiders'].map({'Yes':1, 'No':0})
df['edema'] = df['edema'].map({'Yes':1, 'No':0})
df['gender'] = df['gender'].map({'Male':1, 'Female':0})

X = df[['age','gender','bilirubin','albumin','copper','alk_phos','sgot','platelets',
        'prothrombin','ascites','hepatomegaly','spiders','edema']]
y = df['stage']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)


with open('model.pkl','wb') as f:
    pickle.dump(clf,f)

print("Model trained! Accuracy:", clf.score(X_test,y_test))
