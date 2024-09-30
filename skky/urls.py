from django.urls import path
from skky import views  # views.py에서 정의한 로그인 뷰를 가져옴

urlpatterns = [
    
    path('', views.main, name='main'),  # 메인 페이지로 리디렉션 (임시로 main view가 필요)
    path("login/", views.login_action, name='login'),  # 로그인 URL 추가
    path("signup/", views.signup, name='signup'), # 회원가입 URL 추가
    path("logout/", views.logout_action, name='logout'),
    path('aboutus/', views.aboutus, name='aboutus'),
    
    #################### 관리자 ver ####################
    path('machine/', views.machine, name='기계정보'), 
    path('machine/collect/<int:machine_id>/', views.collect_machine, name='기계수거'),  # 수거 완료 URL 추가
    path('machine/edit/<int:machine_id>/', views.machine_edit, name='기계수정'),
    
    path('user/',views.user, name='회원정보'),
    path('user/delete/<int:user_id>/', views.delete_user, name='탈퇴'),
    path('user/detail/<int:user_id>/', views.user_detail, name='회원상세정보'),
    
    path('product/', views.product, name='상품정보'),
    path('product/upload/', views.product_upload, name='상품등록'),
    path('product/delete/<int:product_id>/', views.product_delete, name='상품삭제'),
    path('product/edit/<int:product_id>/', views.product_edit, name='상품수정'),
    path("reg_gift/", views.reg_gift, name='교환신청내역'),
    path("delivery_complete/<int:exchange_id>/", views.delivery_complete, name='배송완료'),
    path("reward_plus", views.update_product_change, name='교환수량업데이트'),
    
    
    #################### 사용자 ver ####################
    path("mypage/", views.mypage, name='마이페이지'),
    # path('user/delete/<int:user_id>/', views.delete_user, name='탈퇴'),
    path("update_phone/", views.update_phone, name='정보수정'),
    path('reward/', views.reward, name='교환신청'), # 상품이랑 개수만 선택
    path('reward_action', views.reward_action, name='교환신청액션'), # 수령 방법, 주소 등 입력 폼
    path('reward_action_action', views.reward_action_action, name='교환신청제출'), # 폼 액션
    



          
]
