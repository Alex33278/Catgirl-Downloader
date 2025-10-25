A6='zoomed'
A5='300x300'
A4='Everything'
A3='FAILED'
A2='Catgirl Downloader'
A1='store_true'
A0=ImportError
q='SS_IMG'
p='SS_IMG_INFO'
o='CE'
n='MAX'
m='WIN_SIZE'
l='NSFW'
k='Save'
j='images'
i=open
b='SS'
a='About Art'
Z='Refresh'
Y=Exception
T='disabled'
Q='preferences.cgd.json'
P=True
J='normal'
G=print
B=False
F=None
c='1.4'
import argparse as A7,sys as L,os as C
C.chdir(C.path.dirname(C.path.abspath(__file__)))
L.argv[0]=__file__
def r():C.execv(L.executable,['python3']+L.argv)
d=A7.ArgumentParser(prog=f"Catgirl Downloader V{c}",description='Little python script to display some catgirls!')
d.add_argument('--reinstall',action=A1,help='Force reinstalls all packages.')
d.add_argument('--flush_cache',action=A1,help='Flushes the cache.')
s=d.parse_args()
try:
	if s.reinstall:raise A0
	import tkinter,tkinter.filedialog,requests as t,queue as u,webbrowser as A8,threading as A9,base64 as v,random,io;from PIL import Image,ImageTk as w
	try:import orjson as U
	except:import json as U
	try:import requests_cache as AA
	except:pass
except A0:
	import importlib as AB;import tkinter.messagebox
	if tkinter.messagebox.askyesno(A2,'Missing imports! Would you like to download them now?'):
		C.system('pip install pillow');C.system('pip install requests');C.system('pip install orjson');C.system('pip install requests_cache');AB.invalidate_caches()
		if s.reinstall:G('Reinstall successful, you can re-run the program now.');L.exit(0)
		r()
	L.exit(0)
A=tkinter.Tk()
A.wm_title(f"Catgirl Downloader V{c}")
A.wm_geometry('800x800')
A.wm_minsize(300,350)
class AC(tkinter.Canvas):
	def __init__(A,master,**B):super().__init__(master,**B);A.source_image=F;A.image_id=F;A.image=F;A.width,A.height=0,0;A.center_x,A.center_y=0,0;A.bind('<Configure>',A.update_values)
	def update_values(A,*B):
		A.width=A.winfo_width();A.height=A.winfo_height();A.center_x=A.width//2;A.center_y=A.height//2
		if A.image is F:return
		A.delete_previous_image();A.resize_image();A.paste_image()
	def delete_previous_image(A):
		if A.image is F:return
		A.delete(A.image_id);A.image=A.image_id=F
	def resize_image(A):B,C=A.source_image.size;E=A.width/B;F=A.height/C;D=min(E,F);G=int(B*D);H=int(C*D);I=A.source_image.resize((G,H));A.image=w.PhotoImage(I)
	def paste_image(A):A.image_id=A.create_image(A.center_x,A.center_y,anchor=tkinter.CENTER,image=A.image)
	def open_image(A,img):
		A.delete_previous_image();A.source_image=Image.open(img);A.image=w.PhotoImage(A.source_image);A.extension=F
		try:A.extension=A.source_image.format
		except:G('Failed to identify img extension')
		A.resize_image();A.paste_image()
	def open_image_bytes(A,bytes):A.open_image(io.BytesIO(bytes))
K=tkinter.StringVar(value='Block')
V=tkinter.BooleanVar(value=P)
H=F
e=P
M=B
D=F
x=u.Queue()
N='requests_cache'in L.modules
W=tkinter.BooleanVar(value=B)
R=F
def y():
	global R;global N
	if N:R=AA.CachedSession('CGD_IMG_CACHE',expire_after=86400)
def z():
	if N and R:R.close()
def AD():
	A='CGD_IMG_CACHE.sqlite'
	if C.path.exists(A):z();C.remove(A);G('Cache flushed successfully');y()
	else:G('No cache found - did nothing')
y()
def AE(nsfw=B):
	try:
		A=t.get(f"https://nekos.moe/api/v1/random/image?nsfw={str(nsfw).lower()}&count=1",timeout=10)
		if A.status_code==200:return A.text
		else:return
	except Y as B:G(B);return
def AF(response):
	A=response
	if A:global H;B=U.loads(A);H=B;return f"https://nekos.moe/image/{B[j][0]["id"]}"
def AG(nsfw=B):return AF(AE(nsfw))
def AH(url,cache):
	A=url
	if A:
		B=F
		if cache and N:B=R.get(A,timeout=20)
		else:B=t.get(A,timeout=20)
		return B.content
def AI(results,nsfw,cache):
	A=results;global D;global M
	try:
		D=AH(AG(nsfw),cache)
		if D:A.put(D)
		else:A.put(A3)
	except Y as C:G(f"Failed to display image! {C}");E.entryconfigure(Z,state=J);M=B
def f():
	global M
	if M:return
	E.entryconfigure(Z,state=T);M=P;A=B
	if K.get()=='Only':A=P
	if K.get()==A4:A=random.random()>.5
	A9.Thread(target=AI,args=(x,A,W.get()),daemon=P).start()
def AJ():G='https://nekos.moe';F='Arial';E='hyperlink';D=tkinter.Toplevel();D.wm_title('About');D.wm_geometry(A5);D.wm_resizable(B,B);H=tkinter.Label(D,text=A2,font=(F,24));H.pack();I=tkinter.Label(D,text=f"Version {c}");I.pack();C=tkinter.Text(D,wrap=tkinter.WORD,width=40);C.pack();C.insert(tkinter.END,'All images are from ');C.insert(tkinter.END,G,E);C.insert(tkinter.END,'. Licensed under the GNU GENERAL PUBLIC LICENSE V3');C.tag_configure(E,foreground='blue',underline=1);C.tag_bind(E,'<Button-1>',lambda e:A8.open_new_tab(G));C.tag_bind(E,'<Enter>',lambda e:C.configure(cursor='hand2'));C.tag_bind(E,'<Leave>',lambda e:C.configure(cursor=''));C.configure(state=T,relief='flat',borderwidth=0,highlightthickness=0,bg=D.cget('bg'),font=(F,10));D.grab_set();D.transient(A)
def AK():
	if not H:return
	C=tkinter.Toplevel();C.wm_title(a);C.wm_geometry(A5);C.wm_resizable(B,B);D=tkinter.Label(C,text=f"Artist: {H[j][0]["artist"]}\n\nTags: {", ".join(H[j][0]["tags"])}",wraplength=300);D.pack();C.grab_set();C.transient(A)
def AL():
	if not D:return
	A='JPEG'
	if O.extension:A=O.extension
	if not(C:=tkinter.filedialog.asksaveasfilename(title='Save Image As',filetypes=[(f"{A} files",f"*.{A.lower()}"),('All files','*.*')],defaultextension=f".{A.lower()}",initialfile='catgirl')):return
	with i(C,'wb')as B:B.write(D);B.close()
def AM():
	if C.path.isfile(Q):C.remove(Q);r()
E=tkinter.Menu(A,tearoff=0)
I=tkinter.Menu(E,tearoff=0)
X=tkinter.Menu(I,tearoff=0)
X.add_radiobutton(label='Block',variable=K)
X.add_radiobutton(label='Only',variable=K)
X.add_radiobutton(label=A4,variable=K)
I.add_cascade(label='NSFW Settings',menu=X)
I.add_checkbutton(label='Save Session',variable=V)
I.add_checkbutton(label='Cache Enabled',variable=W,state=J if N else T)
I.add_separator()
I.add_command(label='Reset Preferences',command=AM)
I.add_command(label='Flush Cache',command=AD)
E.add_cascade(label='Preferences',menu=I)
S=tkinter.Menu(E,tearoff=0)
S.add_command(label=a,command=AK,state=T)
S.add_command(label='About Catgirl Downloader',command=AJ)
E.add_cascade(label='Help',menu=S)
E.add_command(label=k,command=AL,state=T)
E.add_command(label=Z,command=f)
A.config(menu=E)
def g(msg):B=tkinter.Label(A,text=msg,background='#1F1F1F',foreground='white');B.place(x=A.winfo_width()/2-200,y=50,width=400,height=50);A.after(5000,B.destroy)
def AN():
	F='utf-8';G=A.wm_state()==A6;A.wm_state(J);B={l:K.get(),m:A.geometry().split('+')[0],n:G,o:W.get(),b:V.get()}
	if B[b]:B[p]=H;B[q]=v.b85encode(D).decode(F)
	C=U.dumps(B)
	if isinstance(C,str):C=C.encode(F)
	with i(Q,'wb')as E:E.write(C);E.close()
def AO():
	global D;global H
	if C.path.isfile(Q):
		try:
			B=F
			with i(Q,'r')as I:B=U.loads(I.read())
			if l in B:K.set(B[l])
			if m in B:A.wm_geometry(B[m].split('+')[0])
			if n in B and B[n]:A.wm_state(A6)
			if o in B and N:W.set(B[o])
			if b in B:
				V.set(B[b])
				if p in B:H=B[p];S.entryconfigure(a,state=J)
				if q in B:D=v.b85decode(B[q]);O.open_image_bytes(D);E.entryconfigure(k,state=J)
		except Y as L:G(f"Error loading preferences! {L}");g('Error loading preferences');return
def AP():global e;e=B;z();AN();A.destroy()
O=AC(A)
O.pack(expand=P,fill='both')
A.update()
O.update_values()
AO()
if not(V.get()and C.path.exists(Q)):f()
A.protocol('WM_DELETE_WINDOW',AP)
A.bind('<space>',lambda e:f())
while e:
	A.update()
	try:
		h=x.get_nowait()
		if h and h!=A3:D=h;O.open_image_bytes(D);E.entryconfigure(k,state=J);S.entryconfigure(a,state=J)
		else:G('FAILED TO GET IMAGE');g('Error occured fetching image')
		E.entryconfigure(Z,state=J);M=B
	except u.Empty:pass
	except Y as AQ:G('Unexpected exception occured! '+AQ);g('Unexpected exception occured')