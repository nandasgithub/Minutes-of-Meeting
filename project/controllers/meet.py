import os
import time
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())
@auth.requires_login()
def mycal():
    rows=db(db.t_appointment.created_by==auth.user.id).select()
    return dict(rows=rows)

def index():
	return dict()

@auth.requires_login()
def first():
    user='%(first_name)s'%auth.user
    print "first"
    tb1=DB['user_list']
    test=DB().select(tb1.ALL ,orderby=tb1.id)
    for i in test:
	    if i.user_name == user:
	    	print user is i.user_name
	    	print "user found in user_list"
	    	redirect(URL('index'))
    tb1=DB['user_list']
    test=DB().select(tb1.ALL ,orderby=tb1.id)
    tb2=DB['moderator_list']
    form = SQLFORM.factory(Field('meeting_name',requires=IS_NOT_EMPTY()),Field('subject',requires=IS_NOT_EMPTY()),Field('location',requires=IS_NOT_EMPTY()),Field('date'),Field('already_registered','boolean'))
    if form.process().accepted:
        name = form.vars.meeting_name
	if form.vars.already_registered == True:
		redirect(URL('fourth',vars=dict(name=name)))
	name = form.vars.meeting_name
	print "first",DB.tables
	tb=DB['meeting_list']
	tb.insert(meeting_name=name,moderator_name=user,subject=form.vars.subject,location=form.vars.location,date=form.vars.date)
	if name not in DB.tables:
	    DB.define_table(name,Field('user_name','string',requires=IS_NOT_EMPTY()),
			    Field('body','text', requires=IS_NOT_EMPTY()),Field('time','string'),migrate=True)#,format=lambda r: r.name or 'anonymous')
	    DB.define_table(name+'_'+'names',Field('user_name','string', requires=IS_NOT_EMPTY()),migrate=True)
	    DB.define_table(name+'_'+'users',Field('user_name','string', requires=IS_NOT_EMPTY()),Field('email',requires=IS_EMAIL()),migrate=True)
	    DB.define_table(name+'_'+'files',Field('user_name','string', requires=IS_NOT_EMPTY()),Field('file','upload'))
	print "&&&&&&&&&&&&&&&&&"
        tb2.insert(user_name=user,meeting_name=name)	
	redirect(URL('fourth',vars=dict(name=name)))
    return dict(form = form)

def second():
     name = request.vars.name or redirect(URL('first'))
     tb = DB[name]
     txt = DB().select(tb.ALL ,orderby=tb.id)
     redirect(URL('fourth',vars=dict(name=name)))


def fourth():
    name = request.vars.name or redirect(URL('first'))
    tb = DB[name]
    tb1 = DB[name+'_'+'names']
    tb2 = DB[name+'_'+'files']
    tb3 = DB[name+'_'+'users']
    form1 = SQLFORM(tb2)
    form = SQLFORM.factory(Field('user_name','string',requires=IS_IN_DB(DB,tb3.user_name)),Field('body','text',requires=IS_NOT_EMPTY()))
    form3 = SQLFORM.factory(Field('meeting_name',requires=IS_NOT_EMPTY()))
		
    if form.process(formname='form').accepted:
	tb.insert(user_name=form.vars.user_name,body=form.vars.body,time=time.strftime("%d-%a/%H:%M:%S"))
        response.flash = T("Ur notes is updated!")
    if form1.process(formname='form_one').accepted:
        response.flash = T("Ur file is uploaded!")	
    text = DB().select(tb.ALL ,orderby=tb.id)
    names = DB().select(tb1.ALL,orderby=tb1.id)
    if form3.process().accepted:
	redirect (URL('emailusers', vars={'meeting_name': form3.vars.meeting_name}))
    return dict(text = text,name=name,names=names,form=form,form1=form1,form3=form3)

def startmeeting():
    import time
    session.b=time.strftime("%H:%M:%S")
    a=session.b
    name = request.vars.name
    tb = DB[name]
    tb1 = DB[name+'_'+'names']
    text = DB().select(tb.ALL ,orderby=tb.id)
    names = DB().select(tb1.ALL,orderby=tb1.id)
    return dict(text = text,name=name,names=names,a=a)


def fileupload():
	form = SQLFORM.factory(Field('file','upload',uploadfolder=os.path.join(request.folder,'uploads')),Field('user_name',requires=IS_NOT_EMPTY()))
 	if form.vars.file and form.process().accepted:
            response.flash = T("Ur file is uploaded!")
	return dict(form=form)

def sixth():
    name = request.get_vars['start'].split('/')
    tb = DB[name[0]]
    print name[0]
    j = tb(int(name[1])) or redirect(URL('fourth'))
    print "sixth",j
    return dict(name=j)

def seventh():
    name = request.get_vars['start'].split('/')
    tb = DB[name[0]]
    tb.insert(body=name[1],user_name=name[2])
    text = DB().select(tb.ALL ,orderby=tb.id)
    name = name[0]
    return dict(text=text,name=name)

def eight():
    name = request.get_vars['start'].split('/')
    tb = DB[name[0]]
    txt = DB().select(tb.ALL ,orderby=tb.id)
    return dict(text=txt,name=name[1])

def ninth():
    print "*********"
    user=request.args[0]
    meeting=request.args[1]
    print user +"to be added to" +meeting
    table_name=meeting+'_names'
    print "table name is"+table_name
    tb = DB[table_name]
    text = DB().select(tb.ALL ,orderby=tb.id)
    print "text is"
    flag=0
    for i in text:
        if i.user_name == user:	
	    print "check22"
	    flag=1
            print "flag set"
    print "check3333"
    session.flash=T("user added to the meeting")	

    if flag == 0:	
        print "flag is 0"
	tb.insert(user_name=user)
    	response.flash=T("user added to the meeting")	
    return dict(text = text) 


@auth.requires_login()

def tenth():
	user='%(first_name)s'%auth.user
        tb1=DB['moderator_list']
	test=DB().select(tb1.ALL ,orderby=tb1.id)
	for i in test:
	        if i.user_name == user:
	                redirect(URL('index'))
	print user	
	tb2=DB['user_list']
	tb2.insert(user_name=user)
	table_name=user
	response.flash=T('check1')
	if table_name not in DB.tables:
             DB.define_table(table_name,Field('meetings'))
	form = SQLFORM.factory(Field('register_to_meeting',requires=IS_NOT_EMPTY()),Field('email',requires=IS_EMAIL()))
	if form.process().accepted:
		name=form.vars.register_to_meeting
		emailid=form.vars.email
		response.flash=T(name)
		response.flash=T('check2')
		meet_name=name+'_'+'users'
		if meet_name not in DB.tables:
			response.flash=T('Meeting not registered')
		else:
			tb=DB[name+'_'+'users']
			tb.insert(user_name=user,email=emailid)
			response.flash=T('registration successful')
		print user+'i am user'
	session.list=[]
	temp=[]
	tb2=DB['meeting_list']
	text2=DB().select(tb2.ALL ,orderby=tb2.id)
	for i in text2:
		print i.meeting_list.meeting_name
		j=i.meeting_list.meeting_name+'_users'
		tb3=DB[j]
		text3=DB().select(tb3.ALL ,orderby=tb3.id)
		for p in text3:
			if p.user_name == user:
				temp.append(user)
				temp.append(i.meeting_list.meeting_name)
				session.list.append(temp)
				print user + " in " + i.meeting_list.meeting_name 

	return dict(form=form)

def search():
	return dict()

def adduser():
	meeting_name=request.vars.meeting_name	
	session.meeting_name=meeting_name
	print "addusr",meeting_name
	meeting_name=meeting_name+'_users'
	tb=DB[meeting_name]
	text = DB().select(tb.ALL ,orderby=tb.id)
	session.list=[]
	for row in text:
		flag=0
		for i in session.list:
			if i == row.user_name:
				flag=1
	        if flag is 0:
			print row.user_name
			session.list.append(row.user_name)
        return dict()

def meets():
	tb=DB['meeting_list']
	text=DB().select(tb.ALL,orderby=tb.id)
	return dict(text=text)


def showmeet():
    name = request.get_vars['start']
    print "check",name
    tb=DB['meeting_list']
    n=int(name) 
    print n 
    text=DB().select(tb.ALL,orderby=tb.id)
    for i in text:
	    print i.meeting_list.id
	    if i.meeting_list.id == n:	
		name=i	
	        print "row found"
    return dict(name=name)

def emailusers():
	 user='%(first_name)s'%auth.user
	 meet=request.vars.meeting_name
	 form1 = SQLFORM.factory(Field('body','text',requires=IS_NOT_EMPTY()))
	 if form1.process().accepted:
	 	redirect (URL('email', vars={'meeting_name': meet ,'body':form1.vars.body }))
	 tb=DB['moderator_list']
	 test=DB().select(tb.ALL,orderby=tb.id)
	 tb2=DB[meet]
    	 text=DB().select(tb2.ALL,orderby=tb2.id)
	 return dict(form1=form1,text=text,meeting_name=meet)

def email():
	   meet=request.vars.meeting_name
	   body=request.vars.body
	   name=meet+'_users'
	   tb=DB[name]
	   text=DB().select(tb.ALL,orderby=tb.id)
	   list=[]
	   for i in text:
	   	print "emai is " +i.email
	   	list.append(i.email)
	   print list
	   from gluon.tools import Mail
           mail = Mail()
           mail.settings.server = 'students.iiit.ac.in:25'
           mail.settings.sender = 'srikailash.gandebathula@students.iiit.ac.in'
           mail.settings.login = 'srikailash.gandebathula:24101995'
	   for i in list:
		mail.send(to=[i],subject='Regarding '+meet, message=body)
	   redirect (URL('index'))
