from django.urls import path
from . import views

urlpatterns = [  
    path('loginPage/',views.loginPage,name="login_page"),
    path('logout/',views.logoutuser,name="logout_page"),
    path('updateUser/',views.UpdateUser,name="UpdateUser"),
    path('recentActivities/',views.recentActivities,name="recentActivities"),

    path('settings',views.setting,name="settings"),
    path('',views.home,name="home"),
    path('room/<str:pk>/',views.room,name="room" ),
    path('createRoom/',views.createRoom,name="create_room"),
    path('userProfile/<str:pk>/',views.userProfile,name="userProfile"),
    path('UpdateRoom/<str:pk>/',views.UpdateRoom,name="update_room"),
    path('deleteroom/<str:pk>/,',views.deleteRoom,name="delete-room"),
    path('deletemessage/<str:pk>/,',views.deleteMessage,name="delete-message"),
    path('register/',views.registerPage,name="register"),
    path('topics/',views.topics,name="topics"),
]