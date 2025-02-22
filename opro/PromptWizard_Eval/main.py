import os, json, time
from opro_async import eval_opro
import asyncio

prompt_testing_scores = None
CWD = "./"
TESTING_SCORES_PATH = f"{CWD}testingSetScores.json"

PROMPT_GSM8K = [
    "Answer the following question: {TEXT}",
    """Analyze the given real - world mathematical problem step - by - step ,
identifying key information , relationships between different
pieces of data , and the context . Understand the structure of the
problem , whether it involves a sequence of events or a comparison
between different quantities . Keep track of all variables and
quantities mentioned in the problem . Use appropriate mathematical
operations and formulas , including addition , subtraction ,
multiplication , division , and more complex operations if required .
Understand and handle indirect relationships and different units
of measurement . Apply specific rules or conditions given in the
problem . Make assumptions when information is not explicitly
provided . Consider the order of operations when performing
calculations . Understand the structure and properties of the data
in the problem . Finally , verify your answer against the original
problem to ensure it is logical and accurate .

[ Question ] Tim rides his bike back and forth to work for each of his 5
workdays . His work is 20 miles away . He also goes for a weekend
bike ride of 200 miles . If he can bike at 25 mph how much time
does he spend biking a week ?
[ Answer ] 1. Identify the key pieces of information : Tim bikes to work
and back for 5 days , his work is 20 miles away , he goes for a 200 -
mile bike ride on the weekend , and his biking speed is 25 mph .
2. Understand that the problem involves a sequence of events : Tim ’ s
daily commute to work and back , and his weekend bike ride .
3. Calculate the total distance Tim bikes to work and back in a week :
20 miles to work * 2 ( for the return trip ) = 40 miles per day .
Multiply this by 5 days : 40 miles / day * 5 days = 200 miles .
4. Add the distance of Tim ’ s weekend bike ride to the total distance
he bikes to work : 200 miles ( work ) + 200 miles ( weekend ) = 400
miles .
5. Understand that the problem asks for the total time Tim spends
biking in a week , and that time can be calculated by dividing
distance by speed .
6. Calculate the total time Tim spends biking in a week : 400 miles ÷
25 mph = 16 hours .
7. Verify that the answer is logical : Tim spends 16 hours biking in a
week , which is reasonable given the distances and speed provided .
8. The final answer is 16 hours . < ANS_START >16 < ANS_END >
[ Question ] Tobias is buying a new pair of shoes that costs $95 . He has
been saving up his money each month for the past three months . He
gets a $5 allowance a month . He also mows lawns and shovels
driveways . He charges $15 to mow a lawn and $7 to shovel . After
buying the shoes , he has $15 in change . If he mows 4 lawns , how
many driveways did he shovel ?
[ Answer ] 1. Identify the total amount of money Tobias had before
buying the shoes . This is given by the cost of the shoes plus the
change he has left , which is $95 + $15 = $110 .
2. Calculate the total amount of money Tobias earned from his
allowance . He gets $5 a month and has been saving for three months
, so he earned $5 * 3 = $15 from his allowance .
3. Calculate the total amount of money Tobias earned from mowing lawns
. He charges $15 to mow a lawn and he mowed 4 lawns , so he earned
$15 * 4 = $60 from mowing lawns .
4. Subtract the money Tobias earned from his allowance and mowing
lawns from the total amount of money he had before buying the
shoes . This will give us the amount of money he earned from
shoveling driveways . So , $110 - $15 - $60 = $35 is the amount he
earned from shoveling driveways .
5. Finally , divide the total amount of money Tobias earned from
shoveling driveways by the amount he charges to shovel one
driveway . This will give us the number of driveways he shoveled .
So , $35 / $7 = 5 driveways . < ANS_START >5 < ANS_END >

[ Question ] Bella bought stamps at the post office . Some of the stamps
had a snowflake design , some had a truck design , and some had a
rose design . Bella bought 11 snowflake stamps . She bought 9 more
truck stamps than snowflake stamps , and 13 fewer rose stamps than
truck stamps . How many stamps did Bella buy in all ?
[ Answer ] 1. Identify the quantities given in the problem : Bella bought
11 snowflake stamps .
2. Understand the relationships between the different types of stamps :
She bought 9 more truck stamps than snowflake stamps , and 13
fewer rose stamps than truck stamps .
3. Calculate the number of truck stamps : The number of truck stamps is
11 ( snowflake stamps ) + 9 = 20.
4. Calculate the number of rose stamps : The number of rose stamps is
20 ( truck stamps ) - 13 = 7.
5. Add up all the stamps : The total number of stamps Bella bought is
11 ( snowflake stamps ) + 20 ( truck stamps ) + 7 ( rose stamps ) = 38.
6. Verify the answer : Check that the total number of stamps (38)
matches the sum of the individual quantities of each type of stamp
(11 snowflake stamps , 20 truck stamps , 7 rose stamps ) . The answer
is correct . < ANS_START >38 < ANS_END >

[ Question ] Tina makes $18 .00 an hour . If she works more than 8 hours
per shift , she is eligible for overtime , which is paid by your
hourly wage + 1/2 your hourly wage . If she works 10 hours every
day for 5 days , how much money does she make ?
[ Answer ] 1. Identify the key information : Tina ’ s hourly wage is \ $18
.00 , she works 10 hours a day for 5 days , and overtime is
calculated as the hourly wage plus half the hourly wage for hours
worked over 8 hours in a shift .
2. Calculate the regular pay : Tina works 10 hours a day , but only 8
hours are considered regular hours . So , for 5 days , she works 8
hours / day * 5 days = 40 hours .
3. Multiply the regular hours by the hourly wage to get the regular
pay : 40 hours * $18 .00/ hour = $720 .00.
4. Calculate the overtime hours : Tina works 10 hours a day , so she has
10 hours / day - 8 hours / day = 2 hours / day of overtime . Over 5 days
, this is 2 hours / day * 5 days = 10 hours of overtime .
5. Calculate the overtime wage : The overtime wage is the hourly wage
plus half the hourly wage , so $18 .00/ hour + 0.5 * $18 .00/ hour =
$27 .00/ hour .
6. Multiply the overtime hours by the overtime wage to get the
overtime pay : 10 hours * $27 .00/ hour = $270 .00.
7. Add the regular pay and the overtime pay to get the total pay : $720
.00 + $270 .00 = $990 .00.
8. Verify the answer : Tina makes $990 .00 if she works 10 hours a day
for 5 days , with overtime pay for hours worked over 8 hours in a
shift . This is logical and matches the original problem . <
ANS_START >990 < ANS_END >

[ Question ] Samantha ’ s last name has three fewer letters than Bobbie ’ s
last name . If Bobbie took two letters off her last name , she would
have a last name twice the length of Jamie ’ s . Jamie ’ s full name
is Jamie Grey . How many letters are in Samantha ’ s last name ?
[ Answer ] 1. Start by identifying the key pieces of information from
the problem : Samantha ’ s last name has three fewer letters than
Bobbie ’ s last name , and if Bobbie took two letters off her last
name , she would have a last name twice the length of Jamie ’ s.
Jamie ’ s full name is Jamie Grey .
2. From the information given , we know that Jamie ’ s last name is Grey ,
which has 4 letters .
3. Since Bobbie ’s last name , after removing two letters , is twice the
length of Jamie ’ s last name , we can set up the equation : ( Bobbie ’ s
last name length - 2) = 2 * Jamie ’ s last name length .
4. Substituting the known value of Jamie ’ s last name length (4) into
the equation gives : ( Bobbie ’ s last name length - 2) = 2 * 4 , which
simplifies to Bobbie ’ s last name length - 2 = 8.
5. Solving for Bobbie ’ s last name length gives : Bobbie ’ s last name
length = 8 + 2 = 10.
6. We know that Samantha ’ s last name has three fewer letters than
Bobbie ’ s last name . So , we can set up the equation : Samantha ’ s
last name length = Bobbie ’ s last name length - 3.
7. Substituting the known value of Bobbie ’ s last name length (10) into
the equation gives : Samantha ’ s last name length = 10 - 3.
8. Solving for Samantha ’ s last name length gives : Samantha ’ s last name
length = 7.
9. Therefore , Samantha ’ s last name has 7 letters . < ANS_START >7 < ANS_END
>

< human intent >

Mathematical Reasoning , Multi - step Problem Solving , Basic Arithmetic
Operations , Data Analysis , Solution Verification

< expert persona >

You are a mathematics educator with a deep understanding of elementary
and middle school mathematics . You are experienced in teaching
multi - step problem - solving techniques and have a knack for
breaking down complex problems into manageable steps . Your
expertise lies in basic arithmetic operations such as addition ,
subtraction , multiplication , and division . You can provide clear ,
step - by - step solutions to mathematical problems that require multi
- step reasoning . You are patient and thorough , ensuring that each
step is clearly explained and understood . Your ability to simplify
complex problems and guide students through the problem - solving
process makes you an excellent resource for answering school - grade
mathematical questions .

< prompt guidelines for desired output format >

You need to answer each of the questions separately . Arabic numeral
should be at the end in the format Wrap your only the final answer, 
without reason for each question separately between < ANS_START >
and < ANS_END > tags.

{TEXT}
"""
]

PROMPT_ETHOS = [
    """Carefully examine the provided text and determine if it constitutes
hate speech . Hate speech is defined as language that is derogatory
, offensive , or discriminatory towards a specific group of people
based on their race , gender , or other characteristics , with the
intent to harm or degrade . Even if the statement appears factual
or sarcastic , if it uses aggressive language or personal attacks
aimed at a specific group , it should be classified as hate speech.

[ Question ] While I appreciate the hard work of some immigrants , others
are just here to exploit our system and take our jobs .
[ Answer ] 1. Start by reading the provided text to understand its
content .
2. The task requires identifying if the text contains hate speech .
According to the task description , hate speech is language that is
derogatory , offensive , or discriminatory towards a specific group
of people based on their race , gender , or other characteristics ,
with the intent to harm or degrade .
3. The text states , " While I appreciate the hard work of some
immigrants , others are just here to exploit our system and take
our jobs ."
4. This statement is making a generalization about a specific group of
people , in this case , immigrants . It suggests that some
immigrants are exploiting the system and taking jobs , which is a
negative stereotype .
5. Even though the text acknowledges the hard work of some immigrants ,
it still uses derogatory language towards others , implying they
are here to exploit the system .
6. This statement can be seen as offensive and discriminatory towards
immigrants , as it negatively stereotypes them and can potentially
harm or degrade them .
7. Therefore , according to the task description and instruction , this
text can be classified as hate speech .\ newline
8. As per the task instruction , if the text contains hate speech , the
output should be 1.
9. Hence , the final answer is 1. < ANS_START >1 < ANS_END >

[ Question ] I ’ ve noticed that female politicians are more corrupt and
only care about their own interests .\ newline
[ Answer ] 1. Start by reading the provided text : "I ’ ve noticed that
female politicians are more corrupt and only care about their own
interests ."
2. Identify the subject of the text : The subject is " female
politicians ."
3. Analyze the language used in the text : The language used is
derogatory and offensive , as it generalizes all female politicians
as being " more corrupt " and only caring about their own interests
 Determine if the language is discriminatory : The language
discriminates against a specific group , in this case , female
politicians , by making a negative generalization about them .
5. Check if the language has the intent to harm or degrade : The
language used seems to degrade the reputation of female
politicians by portraying them as corrupt and self - interested .
6. Based on the task description and instruction , the text is
considered hate speech if it is derogatory , offensive , or
discriminatory towards a specific group of people with the intent
to harm or degrade .
7. Since the text meets all these criteria , it is classified as hate
speech .
8. According to the task instruction , if the text contains hate speech
, the output should be 1.
9. Therefore , the final answer is 1. < ANS_START >1 < ANS_END >

[ Question ] I don ’ t get why we have to accept people who choose to be
transgender . It ’ s unnatural and against our values .
[ Answer ] 1. Start by reading the provided text .
2. Identify the subject of the text . In this case , the subject is "
people who choose to be transgender ."
3. Analyze the language used in the text . The text uses phrases like "
It ’ s unnatural " and " against our values ," which are derogatory and
offensive .
4. Determine if the language is aimed at a specific group . Here , the
language is targeted towards transgender people , a specific group .
5. Check if the language is intended to harm or degrade the specific
group . The text implies that being transgender is unnatural and
against societal values , which can be seen as an attempt to
degrade or harm the transgender community .\ newline
6. Since the text uses offensive language against a specific group
with the intent to harm or degrade , it can be classified as hate
speech .
7. Therefore , the correct answer is 1 , indicating that the text
contains hate speech . < ANS_START >1 < ANS_END >

< human intent >

Text Analysis , Hate Speech Identification , Discriminatory Language
Detection , Offensive Content Recognition , Derogatory Language
Classification

< expert persona >

You are a machine learning engineer with a specialization in natural
language processing and text analysis . You have developed and
trained algorithms to detect and classify different types of text ,
including hate speech . Your algorithm can analyze the given text ,
identify patterns , and determine whether it contains hate speech
or not . You are equipped with a deep understanding of the nuances
of language , and you can differentiate between offensive language ,
strong criticism , and actual hate speech . Your algorithm is
designed to be fair and unbiased , and it respects the principles
of freedom of speech while also recognizing the harm caused by
hate speech . Your expertise in text analysis and machine learning
is highly valuable in moderating online content and creating a
safer digital environment .

< prompt guidelines for desired output format >
You need to answer each of the questions separately with 1 if its a
hate speech and 0 if its not a hate speech . Wrap your only the
final answer , without reason for each question separately between
< ANS_START > and < ANS_END > tags .

{TEXT}
"""
]

PROMPT_PUBMEDQA = [
    """Carefully read the abstract and identify the key points that directly
address the biomedical research question . Based on these key
points , provide a clear and concise answer in a " Yes " or " No "
format , followed by a brief explanation that correlates the
research question with the findings in the abstract .

[ Question ] Does the process of photosynthesis under varying light
intensities and temperature play a significant role in the growth
of different species of algae ?\ newline
[ Abstract ] : Photosynthesis is a process used by plants and other
organisms to convert light energy into chemical energy that can
later be released to fuel the organisms ’ activities . This study
investigates the impact of varying light intensities and
temperature on the photosynthetic process in different species of
algae . The algae were exposed to different light intensities and
temperatures , and their growth rate was monitored over a period of
time . The results showed a direct correlation between light
intensity , temperature and the growth rate of algae .
[ Answer ] 1. The question asks whether the process of photosynthesis
under varying light intensities and temperature plays a
significant role in the growth of different species of algae .
2. The abstract provides information about a study that investigates
the impact of varying light intensities and temperature on the
photosynthetic process in different species of algae .
3. The abstract mentions that the algae were exposed to different
light intensities and temperatures , and their growth rate was
monitored over a period of time .\ newline
4. The results of the study , as mentioned in the abstract , showed a
direct correlation between light intensity , temperature and the
growth rate of algae .
5. This direct correlation indicates that the process of
photosynthesis under varying light intensities and temperature
does indeed play a significant role in the growth of different
species of algae .
6. Therefore , based on the information provided in the abstract , the
answer to the question is " Yes ". < ANS_START > yes < ANS_END >


[ Question ] Is the use of antiviral drugs effective in treating
influenza , a common viral infection ?
[ Abstract ] : Antiviral drugs are medicines used to prevent and treat
viral infections . Influenza , on the other hand , is a viral
infection . This study investigates the effectiveness of antiviral
drugs in treating influenza . The study involved patients suffering
from influenza who were treated with antiviral drugs . The results
showed significant improvement in the condition of the patients .
[ Answer ] 1. The question asks about the effectiveness of antiviral
drugs in treating influenza , a common viral infection .
2. The abstract provides information about a study that investigates
the effectiveness of antiviral drugs in treating influenza .
3. The study involved patients suffering from influenza who were
treated with antiviral drugs .\ newline
4. The results of the study showed significant improvement in the
condition of the patients after they were treated with antiviral
drugs .
5. Therefore , based on the results of the study mentioned in the
abstract , it can be concluded that the use of antiviral drugs is
effective in treating influenza .
6. Hence , the answer to the question is " Yes ". < ANS_START > yes < ANS_END >
[ Question ] Are intensive care units more beneficial than general wards
for the treatment of severe pneumonia in children with underlying
health conditions ?
[ Abstract ] : Pneumonia is a common illness in children that can become
severe if not properly treated . Intensive care units ( ICUs )
provide specialized care for patients with severe or life -
threatening illnesses . This study examines the impact of ICU
treatment on children with severe pneumonia and underlying health
conditions . The study compared the recovery rates of children
treated in ICUs with those treated in general wards . The results
showed a higher recovery rate in children with underlying health
conditions treated in ICUs .\ newline
[ Answer ] 1. The question asks whether intensive care units ( ICUs ) are
more beneficial than general wards for the treatment of severe
pneumonia in children with underlying health conditions .
2. The abstract provides information about a study that examined the
impact of ICU treatment on children with severe pneumonia and
underlying health conditions .\ newline
3. The study compared the recovery rates of children treated in ICUs
with those treated in general wards .
4. The results of the study showed a higher recovery rate in children
with underlying health conditions treated in ICUs .
5. Therefore , based on the results of the study presented in the
abstract , the answer to the question is " Yes ". ICUs are more
beneficial than general wards for the treatment of severe
pneumonia in children with underlying health conditions . <
ANS_START > yes < ANS_END >

[ Question ] Is the blood glucose level a more reliable marker than
HbA1c for diagnosing Diabetes ?
[ Abstract ] : Diabetes is a chronic disease that affects the body ’ s
ability to process sugar . Blood glucose levels and HbA1c are
commonly used markers for diagnosing diabetes . This study
investigates the reliability of blood glucose levels and HbA1c as
markers for diagnosing Diabetes . The study involved patients
diagnosed with Diabetes and their blood glucose and HbA1c levels
were measured . The results showed a significant correlation
between high blood glucose levels and Diabetes diagnosis , but not
with HbA1c levels .
[ Answer ] 1. The question asks whether blood glucose level is a more
reliable marker than HbA1c for diagnosing Diabetes .\ newline
2. The abstract provides information about a study that investigates
the reliability of blood glucose levels and HbA1c as markers for
diagnosing Diabetes .
3. The abstract mentions that the study involved patients diagnosed
with Diabetes and their blood glucose and HbA1c levels were
measured .
4. The key point in the abstract is the results of the study , which
showed a significant correlation between high blood glucose levels
and Diabetes diagnosis , but not with HbA1c levels .
5. This indicates that blood glucose levels are a more reliable marker
for diagnosing Diabetes than HbA1c levels , according to the study.
6. Therefore , based on the information provided in the abstract , the
answer to the question is " Yes ". < ANS_START > yes < ANS_END >


[ Question ] Can regular strength training reduce the risk of
osteoporosis in adults over 60?
[ Abstract ] : Osteoporosis is a major health issue globally , especially
in adults over 60. Regular strength training is known to have
various health benefits , including improving bone health . This
study investigates the impact of regular strength training on the
risk of osteoporosis in adults over 60. The study involved
participants who engaged in regular strength training and their
bone health was monitored over a period of time . The results
showed a lower incidence of osteoporosis in participants who
engaged in regular strength training .
[ Answer ] 1. The question asks whether regular strength training can
reduce the risk of osteoporosis in adults over 60.
2. The abstract provides information about a study that investigates
the impact of regular strength training on the risk of
osteoporosis in adults over 60.
3. The abstract mentions that regular strength training is known to
have various health benefits , including improving bone health .
4. The study involved participants who engaged in regular strength
training and their bone health was monitored over a period of time.
5. The results of the study , as mentioned in the abstract , showed a
lower incidence of osteoporosis in participants who engaged in
regular strength training .
6. Therefore , based on the results of the study mentioned in the
abstract , it can be concluded that regular strength training can
reduce the risk of osteoporosis in adults over 60.
7. Hence , the answer to the question is " Yes ". < ANS_START > yes < ANS_END >

< human intent >
Biomedical Research Understanding , Abstract Analysis , Key Point
Identification , Concise Answering , Explanation Correlation

< expert persona >

You are a biomedical researcher with a deep understanding of medical
and scientific literature . You have a strong background in reading
and interpreting scientific abstracts , and you are skilled at
extracting key information from complex texts . You can accurately
answer biomedical research questions based on the information
provided in the corresponding abstracts . Your expertise in
biomedical research allows you to understand the nuances and
implications of the findings presented in the abstracts , and you
can provide clear , concise , and accurate answers to the questions .
Your ability to critically analyze and interpret scientific
literature makes you an invaluable resource in the field of
biomedical research .

< prompt guidelines for desired output format >

You need to answer each of the questions separately with yes / no /
maybe . Wrap your only the final answer , without reason for each
question separately between < ANS_START > and < ANS_END > tags .

{TEXT}
"""
]

PROMPT_MEDQA = [
    """Analyze the patient ’ s age , symptoms , duration and onset of symptoms ,
history of present illness , lifestyle factors , physical
examination findings , and any diagnostic test results presented in
the Medical Licensing Examination question . Use your knowledge of
medicine to identify the most likely diagnosis or appropriate
treatment . Consider the progression , severity , and duration of the
patient ’ s symptoms in relation to the answer options . Eliminate
incorrect answer options based on your medical knowledge and
ensure your final choice is the most appropriate given the
specifics of the question . Validate your answer by ensuring it
aligns with all the information provided in the question ,
including the patient ’ s age , lifestyle factors , and specific
diagnostic test results .

[ Question ] A 50 - year - old man with a history of hypertension and type 2
diabetes presents with a 3 - day history of chest pain radiating to
the left arm . He also reports shortness of breath and fatigue .
Physical examination reveals a blood pressure of 150/90 mmHg ,
heart rate of 90/ min , and an irregular pulse . An ECG shows ST -
segment elevation in leads II , III , and aVF . Which of the
following is the most appropriate initial treatment ?
Options :
A : Aspirin and clopidogrel
B : Metformin
C : Lisinopril
D : Atorvastatin

[ Answer ] 1. Start by analyzing the patient ’ s age , symptoms , and
medical history . The patient is a 50 - year - old man with a history
of hypertension and type 2 diabetes . He presents with chest pain
radiating to the left arm , shortness of breath , and fatigue . These
symptoms are indicative of a cardiovascular event .
2. Consider the physical examination findings . The patient has a blood
pressure of 150/90 mmHg , heart rate of 90/ min , and an irregular
pulse . These findings further support the likelihood of a
cardiovascular event .
3. Review the diagnostic test results . The ECG shows ST - segment
elevation in leads II , III , and aVF . This is a classic sign of an
ST - segment elevation myocardial infarction ( STEMI ) , a type of
heart attack .
4. Given the diagnosis of STEMI , consider the most appropriate initial
treatment . The options are Aspirin and clopidogrel ( A ) , Metformin
( B ) , Lisinopril ( C ) , and Atorvastatin ( D ) .
5. Eliminate incorrect answer options based on medical knowledge .
Metformin ( B ) is a medication for diabetes , Lisinopril ( C) is an
antihypertensive medication , and Atorvastatin ( D ) is a cholesterol
- lowering medication . While these medications may be part of the
patient ’s long - term management , they are not the most appropriate
initial treatment for a STEMI .
6. Aspirin and clopidogrel ( A ) are antiplatelet medications . They work
by preventing blood clots , which is crucial in the initial
management of a STEMI to restore blood flow to the heart muscle .
7. Therefore , the most appropriate initial treatment for this patient ,
given his symptoms , physical examination findings , and ECG
results , is Aspirin and clopidogrel ( A ). This aligns with all the
information provided in the question and is the most appropriate
given the specifics of the question .
8. Validate the final choice (A ) as it is the most appropriate initial
treatment for a patient presenting with a STEMI . < ANS_START >A <
ANS_END >


[ Question ] A 6 - month - old girl is brought to the physician by her
mother because of a 2 - day history of fever and irritability . She
also has a rash on her cheeks . Physical examination reveals a
temperature of 38.5 ◦
C (101.3 ◦
F ) , a heart rate of 120/ min , and a
respiratory rate of 30/ min . Examination of the skin shows
erythema of the cheeks with sparing of the nasal bridge and
perioral area . Which of the following is the most likely diagnosis
?
Options :
A : Measles
B : Fifth disease
C : Roseola
D : Scarlet fever

[ Answer ] 1. Start by analyzing the patient ’ s age , symptoms , duration
and onset of symptoms , and physical examination findings . The
patient is a 6 - month - old girl with a 2 - day history of fever and
irritability . She also has a rash on her cheeks . Her temperature
is 38.5◦
C (101.3◦
F ) , a heart rate of 120/ min , and a respiratory
rate of 30/ min . The skin examination shows erythema of the cheeks
with sparing of the nasal bridge and perioral area .
2. Use your medical knowledge to identify the most likely diagnosis .
The symptoms presented are indicative of a viral exanthem , a rash
that appears due to a viral infection .
3. Consider the answer options . The options are Measles , Fifth disease
, Roseola , and Scarlet fever . All of these are diseases that can
present with a rash .
4. Eliminate incorrect answer options based on your medical knowledge .
Measles typically presents with a rash that starts at the
hairline and moves down , along with Koplik spots in the mouth ,
which are not mentioned in the question . Scarlet fever typically
presents with a sandpaper - like rash and a strawberry tongue , which
are also not mentioned . Roseola typically presents with a high
fever that suddenly drops as a rash appears , which does not match
the patient ’ s symptoms .
5. The remaining option is Fifth disease , also known as erythema
infectiosum . This disease is common in children and presents with
a " slapped cheek " rash , fever , and irritability , which aligns with
the patient ’ s symptoms .
6. Validate your answer by ensuring it aligns with all the information
provided in the question . The patient ’ s age , symptoms , and
physical examination findings all align with a diagnosis of Fifth
disease .
7. Therefore , the correct answer is B : Fifth disease . < ANS_START >B <
ANS_END >


[ Question ] A 70 - year - old man presents with a 1 - year history of
progressive memory loss , difficulty finding words , and getting
lost in familiar places . Neurologic examination shows impaired
recall and disorientation to time and place . MRI of the brain
shows cortical atrophy and enlarged ventricles . Which of the
following is the most likely diagnosis ?
Options :
A : Alzheimer ’ s disease
B : Vascular dementia
C : Lewy body dementia
D : Frontotemporal dementia

[ Answer ] 1. Start by analyzing the patient ’ s age , symptoms , duration
and onset of symptoms , and the results of the physical examination
and diagnostic tests . The patient is a 70 - year - old man with a 1 -
year history of progressive memory loss , difficulty finding words ,
and getting lost in familiar places . The neurologic examination
shows impaired recall and disorientation to time and place . The
MRI of the brain shows cortical atrophy and enlarged ventricles .
2. Consider the progression , severity , and duration of the patient ’ s
symptoms . The symptoms have been progressing over a year , which
indicates a chronic condition .
3. Use your medical knowledge to identify the most likely diagnosis .
The symptoms of progressive memory loss , difficulty finding words ,
and getting lost in familiar places , along with impaired recall
and disorientation to time and place , are characteristic of a
neurodegenerative disease .
4. Look at the answer options and eliminate incorrect ones based on
your medical knowledge . Vascular dementia ( Option B) typically
presents with stepwise deterioration of cognitive function , which
is not the case here . Lewy body dementia ( Option C ) is usually
accompanied by visual hallucinations , parkinsonism , or fluctuating
cognition , none of which are mentioned in the question .
Frontotemporal dementia ( Option D ) often presents with changes in
personality and behavior , which is also not mentioned in the
question .
5. The remaining option is Alzheimer ’ s disease ( Option A ) , which is a
neurodegenerative disease that commonly presents with progressive
memory loss , difficulty finding words , and getting lost in
familiar places , especially in older adults . The MRI findings of
cortical atrophy and enlarged ventricles are also consistent with
Alzheimer ’ s disease .
6. Validate your answer by ensuring it aligns with all the information
provided in the question . Alzheimer ’ s disease fits with the
patient ’s age , the chronic and progressive nature of the symptoms ,
the neurologic examination findings , and the MRI results .
7. Therefore , the correct answer is A : Alzheimer ’ s disease . < ANS_START
>A < ANS_END >


[ Question ] A 35 - year - old woman presents with a 2 - week history of
severe headache , fever , and photophobia . She also reports a rash
on her lower extremities . Physical examination reveals a
temperature of 38.2◦
C (100.8◦
F ) , a heart rate of 110/ min , and a
petechial rash on her lower extremities . Lumbar puncture shows
increased white blood cells with a predominance of lymphocytes ,
increased protein , and normal glucose . Which of the following is
the most appropriate pharmacotherapy ?
Options :
A : Ceftriaxone and vancomycin
B : Acyclovir
C : Amphotericin B
D : Doxycycline

[ Answer ] 1. Start by analyzing the patient ’ s symptoms : severe headache
, fever , photophobia , and a petechial rash on her lower
extremities . These symptoms suggest a systemic infection , possibly
involving the central nervous system given the presence of
headache and photophobia .
2. Consider the patient ’ s age and duration of symptoms . A 35 - year - old
woman with a 2 - week history of these symptoms suggests an acute
infection rather than a chronic condition .
3. Review the physical examination findings and diagnostic test
results . The patient has a fever and tachycardia , further
supporting the presence of a systemic infection . The lumbar
puncture results show increased white blood cells with a
predominance of lymphocytes , increased protein , and normal glucose
. These findings are indicative of viral meningitis .
4. Evaluate the answer options in relation to the most likely
diagnosis . Viral meningitis is typically caused by enteroviruses ,
herpes simplex virus , or arboviruses .
5. Option A ( Ceftriaxone and vancomycin ) is used to treat bacterial
meningitis , which is not consistent with the lumbar puncture
results . Eliminate this option .
6. Option B ( Acyclovir ) is an antiviral medication used to treat
infections caused by herpes viruses , including herpes simplex
virus meningitis . This option aligns with the diagnosis .
7. Option C ( Amphotericin B ) is an antifungal medication , which is not
consistent with the diagnosis of viral meningitis . Eliminate this
option .
8. Option D ( Doxycycline ) is an antibiotic used to treat bacterial
infections , including certain types of bacterial meningitis , but
it is not the first - line treatment for viral meningitis . Eliminate
this option .
 Validate the final choice ( Option B : Acyclovir ) by ensuring it
aligns with all the information provided in the question ,
including the patient ’ s age , symptoms , physical examination
findings , and specific diagnostic test results .
10. Therefore , the correct answer is B : Acyclovir . < ANS_START >B <
ANS_END >


[ Question ] A 40 - year - old man with a history of alcohol abuse presents
with a 1 - day history of severe abdominal pain , nausea , and
vomiting . Physical examination reveals a distended abdomen ,
decreased bowel sounds , and tenderness to palpation in the upper
abdomen . Laboratory tests show an elevated serum amylase and
lipase . Which of the following is the most likely diagnosis ?
Options :
A : Acute pancreatitis
B : Peptic ulcer disease
C : Gastric cancer
D : Gastroenteritis

[ Answer ] 1. Start by analyzing the patient ’ s age , symptoms , duration
and onset of symptoms , history of present illness , lifestyle
factors , physical examination findings , and any diagnostic test
results presented in the question . The patient is a 40 - year - old
man with a history of alcohol abuse . He has been experiencing
severe abdominal pain , nausea , and vomiting for 1 day . His abdomen
is distended , bowel sounds are decreased , and there is tenderness
in the upper abdomen . His serum amylase and lipase levels are
elevated .
2. Use your knowledge of medicine to identify the most likely
diagnosis . The patient ’ s history of alcohol abuse , the sudden
onset and severity of his symptoms , and his physical examination
findings are all indicative of a pancreatic condition . The
elevated serum amylase and lipase levels further support this , as
these enzymes are produced by the pancreas and their levels
increase in the blood when the pancreas is inflamed or damaged .
3. Consider the answer options in relation to the patient ’ s symptoms
and test results . Acute pancreatitis , peptic ulcer disease ,
gastric cancer , and gastroenteritis are all potential diagnoses .
4. Eliminate incorrect answer options based on your medical knowledge .
Peptic ulcer disease typically presents with a burning pain in
the middle or upper stomach between meals or at night , not with a
distended abdomen and decreased bowel sounds . Gastric cancer
usually develops slowly over many years , and its symptoms often
only appear in the advanced stages of the disease . Gastroenteritis
, while it can cause abdominal pain , nausea , and vomiting , does
not typically result in a distended abdomen , decreased bowel
sounds , or elevated serum amylase and lipase levels .
5. The remaining option , acute pancreatitis , aligns with all the
information provided in the question . The patient ’ s history of
alcohol abuse is a common risk factor for acute pancreatitis . The
sudden onset and severity of his symptoms , his physical
examination findings , and his elevated serum amylase and lipase
levels are all characteristic of this condition .
6. Therefore , the most likely diagnosis for this patient is acute
pancreatitis , making option A the correct answer . < ANS_START >A <
ANS_END >

< human intent >

Medical Knowledge , Analytical Skills , English Proficiency , Reasoning
Skills , Attention to Detail

< expert persona >
You are a medical professional with extensive experience in the field
and a deep understanding of the United States Medical Licensing
Exam ( USMLE ) . You have successfully passed the USMLE and have a
thorough understanding of the format and style of the questions .
You are well - versed in a wide range of medical topics , from
anatomy and physiology to pathology and pharmacology . You have the
ability to analyze complex medical scenarios , apply your
knowledge , and make informed decisions . You can accurately
interpret the questions and the provided options , and select the
correct answer based on your medical knowledge and reasoning . Your
expertise and experience make you highly capable of answering
these questions correctly and efficiently .

< prompt guidelines for desired output format >

You need to output the correct option among [ A / B / C /D ] for each
question separately using your medical knowledge and reasoning .
Wrap your only the final answer , without reason for each question
separately between < ANS_START > and < ANS_END > tags .

{TEXT}
"""
]

async def opro(prompt_list, category):
    global prompt_testing_scores, TESTING_SCORES_PATH
    opro_func = None
    match category:
        case "eval":
            opro_func = eval_opro
        case _:
            raise ValueError(f"Invalid category: {category}")

    # Optimizing Prompts
    for prompt in prompt_list:
        if prompt not in prompt_testing_scores:
            ID = len(prompt_testing_scores)
            # ID = time.time()
            prompt_testing_scores[prompt] = {
                "ID": ID,
                **await opro_func(
                    prompt,
                    f"{CWD}{str(ID)}",
                    # PROMPTS_PER_STEP=1,
                    # TRAINING_SAMPLE_SIZE=30,
                    # TESTING_SAMPLE_SIZE=70,
                    # STEP_COUNT=10,
                    # MAX_PROMPT_SCORE_PAIRS=10,
                ),
                "category": category,
            }

        # Save Prompt Scores
        with open(TESTING_SCORES_PATH, "w") as f:
            json.dump(prompt_testing_scores, f, indent=4)


async def main():
    global prompt_testing_scores, TESTING_SCORES_PATH
    # TRAINING SCORES: stored in directories corresponding to the prompt ID (shown in testingSetScores.json)
    # TESTING SCORES: stored in a single file called testingSetScores.json
    if os.path.exists(TESTING_SCORES_PATH):
        with open(TESTING_SCORES_PATH, "r") as f:
            prompt_testing_scores = json.load(f)
    else:
        prompt_testing_scores = {}

    # Optimizing Prompts
    # await opro(PROMPT_GSM8K, "eval")
    # await opro(PROMPT_ETHOS, "eval")
    # await opro(PROMPT_PUBMEDQA, "eval")
    await opro(PROMPT_MEDQA, "eval")

    # NOTE: Use time.time() as ID if using this approach!
    # await asyncio.gather(
    #     # opro(PROMPT_LIST_TRANS, "translation"),
    #     # opro(PROMPT_LIST_ERR, "error_correction"),
    #     # opro(PROMPT_LIST_SUMM, "summarization")
    #     # opro(PROMPT_LIST_QA, "QA_refinement"),
    # )


if __name__ == "__main__":
    asyncio.run(main())
