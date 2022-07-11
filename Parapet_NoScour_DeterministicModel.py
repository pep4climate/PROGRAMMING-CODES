#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def Parapet_contribution(h_pt):


    # In[1]:


    import math


    # In[2]:


    h_pt = 870/1000 #m
    b_pt = 0.30 #m


    # In[3]:


    h_sw = 0.6 #m
    r_e = 3950/1000 #m
    r_i = 3450/1000 #m
    H_sw = h_sw + r_e #m
    B_p = 1.80 #m
    L = 9260/1000 #m
    t = 500/1000 #m


    # In[4]:


    b = 1 #m 


    # In[5]:


    gamma_pt = 22 #kN/m3


    # In[6]:


    A_pt = 1/2*(L+B_p)*h_pt #m2


    # In[7]:


    P_pt = gamma_pt*b_pt*A_pt #kN
    print(P_pt)


    # In[8]:


    V_a = P_pt #kN


    # In[9]:


    x_pt = (L/2+B_p/2)/2-(B_p/2)


    # In[10]:


    H_c = (x_pt*P_pt)/(2/3*t+r_i)


    # In[11]:


    S_a = math.sqrt(math.pow(H_c,2)+math.pow(V_a,2))
    print(S_a)


    # In[12]:


    gamma_fL = 1.15
    gamma_f_three = 1.0
    e = t/6 #m
    CF = 1
    delta = 0.85
    K = 0.50
    alfa = 0.7
    beta = 0.3
    f_m = 4 #MPa
    fm_b = 8 #MPa


    # In[13]:


    f_b = CF * delta * fm_b #MPa
    f_k = K * math.pow(f_b, alfa) * math.pow(f_m, beta) #MPa
    f_k


    # In[14]:


    R_d = 0.4 * b * f_k * (t-2*e)*1000 #kN
    print(f'{R_d:.2f}')


    # In[15]:


    E_d_pt = gamma_fL * gamma_f_three * S_a #kN
    E_d_pt


    # In[16]:


    E_d_pt <= R_d


    # In[17]:


    return E_d_pt


    # In[ ]:




