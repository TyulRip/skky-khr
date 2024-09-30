from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Machine, MachineUser, User, Product, Exchange, Delivery
import folium
import pandas as pd
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required


### 메인 ##############################
def main(request):
    return render(request, 'main.html')  # 메인 페이지를 렌더링

def aboutus(request):
    return render(request, 'aboutus.html')

### 로그인 ##############################
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 사용자 인증
        user = User.objects.filter(username=username).first()  # username으로 사용자 검색

        if user and user.password == password:  # 비밀번호를 평문으로 비교
            
            #request.session['user_id'] = user.id  # 세션에 사용자 ID 저장
            login(request, user)
            return redirect('main')  # 로그인 성공 후 메인 페이지로 리디렉션
        else:
            messages.error(request, '아이디 또는 비밀번호가 잘못되었습니다.')
            return render(request, 'user/login.html') # 실패 시 로그인 페이지로 돌아감

    return render(request, 'user/login.html')

### 로그아웃
def logout_action(request):
    request.session.flush()
    return redirect('main')
    
### 회원가입 ##############################
def signup(request):
    if request.method == 'POST':
        # 폼에서 사용자 정보 받아오기
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_name = request.POST.get('user_name')
        user_phone = request.POST.get('user_phone')

        # 사용자 정보 유효성 검사
        if not username or not password or not user_name:
            messages.error(request, '아이디, 비밀번호, 이름은 필수입니다.')
            return render(request, 'user/signup.html')
        
        # 중복된 아이디 체크
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 존재하는 아이디입니다.')
            return render(request, 'user/signup.html')

        # 사용자 정보 DB에 저장 (비밀번호 해시화 생략)
        user = User.objects.create(
            username=username,
            password=password,  # 평문 비밀번호 저장
            user_name=user_name,
            user_phone=user_phone
        )
        messages.success(request, '회원가입이 완료되었습니다.')
        return redirect('login')  # 회원가입 후 로그인 페이지로 리디렉션

    # GET 요청 시 회원가입 페이지 렌더링
    return render(request, 'user/signup.html')


############################################ 사용자 ver ############################################

### 마이페이지 ##############################
@login_required
def mypage(request):
    return render(request, 'user/mypage.html')

# 마이페이지 정보 수정 (전화번호)
@login_required
def update_phone(request):
    var_user_phone = request.POST.get('input_user_phone')

    user_object = User.objects.get(id = request.user.id)

    user_object.user_phone = var_user_phone
    user_object.save()

    return redirect('마이페이지')

    
### 교환 신청
def reward(request):
    products = Product.objects.all()  # 모든 상품 조회
    user_points = request.user.user_point  # 사용자의 현재 포인트 가져오기

    # count 최대값
    max_count = []
    
    available_products = []

    for product in products:
        # 사용자의 포인트보다 낮은 상품만
        if product.product_point <= user_points:
            # 교환 가능한 개수 계산
            count = user_points // product.product_point  
            # 1부터 count까지의 리스트 생성
            quantity_options = list(range(1, count + 1))  
            
            max_count.append(count)
            # 상품 정보와 함께 수량 옵션 추가
            available_products.append({
                'id': product.id,
                'name': product.product_name,
                'points': product.product_point,
                'count': count,
                'quantity_options': quantity_options  # 수량 옵션 추가
            })

    # max_count가 비어 있지 않으면 a를 할당
    if max_count:
        a = max(max_count)
    else:
        a = 0  # max_count가 비어 있을 경우 기본값 설정

    b = [i for i in range(1, a + 1)]

    content = {
        "users": request.user,
        "products": products,  # 교환 가능한 상품 목록
        "b": b,
        "available_products": available_products,
    }

    return render(request, 'exchange/exchange.html', content)

def reward_action(request):
    user = request.user
    
    # POST로 전달된 데이터 받기
    product_id = request.POST.get('product')
    quantity = request.POST.get('quantity')
    
    product = Product.objects.get(id=product_id)
    
    return render(request, 'exchange/reward.html', {'user':user,'product':product, 'quantity':quantity})

def reward_action_action(request):
    var_user_id = request.POST.get('user_id')
    var_product_id = request.POST.get('product_id')
    var_product_cnt = request.POST.get('product_cnt')
    var_change_type = request.POST.get('change_type')
    var_address = request.POST.get('address')
    var_datetime = request.POST.get('datetime')

    # 교환 기록 생성
    Exchange.objects.create(user_id=var_user_id,
                            product_id=var_product_id,
                            change_cnt=var_product_cnt,
                            change_way=var_change_type,
                            change_app_dt=var_datetime)
    
    # 배송 요청일 경우 배송 테이블에 추가
    if int(var_change_type) == 1:
        Delivery.objects.create(user_id=var_user_id,
                                product_id=var_product_id,
                                del_status=0,
                                del_address=var_address)

    # 사용자 포인트 업데이트
    user = User.objects.get(id=var_user_id)  # 사용자 객체 가져오기
    product = Product.objects.get(id=var_product_id)  # 상품 객체 가져오기
    
    # 포인트 차감
    user.user_point -= int(product.product_point) * int(var_product_cnt)
    user.save()  # 변경된 값을 저장

    return redirect('main')
    


############################################ 관리자 ver ############################################

# 기계 관리
def machine(request):
    machines = Machine.objects.all()  # 모든 기계 정보 가져오기
    
    # 기계 정보를 JSON으로 변환
    machine_data = []
    for machine in machines:
        machine_data.append({
            'id': machine.id,
            'address': machine.machine_address,
            'capacity': machine.machine_capacity,
            'pet': machine.machine_pet,
            'latitude': machine.machine_latitude,
            'longitude': machine.machine_longitude,
        })
    
    dt = pd.read_csv("skky/data/가상기계설치2.csv")

    # 평균 위도와 경도 계산
    lat = dt['machine_latitude'].mean()
    long = dt['machine_longitude'].mean()

    # Folium 지도 생성
    m = folium.Map([lat, long], zoom_start=15, tiles='OpenStreetMap')
    
    # Folium 마커 추가        
    for machine in machine_data:
        folium.Marker(
            [machine['latitude'], machine['longitude']],
            tooltip=machine['address'],
            icon=folium.Icon(color='blue'),
        ).add_to(m)


    # 지도를 HTML로 저장
    map = m._repr_html_()  # 변수 이름 수정
    
    return render(request, 'manage/machine.html', {'machines': machines, 'map': map, 'machine_data': machine_data})

# 기계 페트병 수거하기
def collect_machine(request, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)  # 기계 객체 가져오기
    machine.machine_pet = 0  # 페트병 수를 0으로 업데이트
    machine.save()  # 변경사항 저장
    return redirect('기계정보')  # 기계 목록 페이지로 리디렉션

# 기계 정보 수정
def machine_edit(request, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)

    if request.method == 'POST':
        machine.machine_address = request.POST.get('machine_address')
        machine.machine_capacity = request.POST.get('machine_capacity')  # 추가된 필드
        machine.machine_pet = request.POST.get('machine_pet')
        machine.save()
        return redirect('기계정보')  # 수정 후 기계 목록 페이지로 리디렉션

    return render(request, 'manage/machine_edit.html', {'machine': machine})

##############################

# 회원 관리
def user(request):
    users = User.objects.filter(user_grade__gt=0)
    return render(request, 'manage/user.html', {'users':users})

# 회원 삭제
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)  # 기계 객체 가져오기
    user.user_del = 1  # 페트병 수를 0으로 업데이트
    user.save()  # 변경사항 저장
    return redirect('회원정보')  # 회원 목록 페이지로 리디렉션

# 회원 상세 정보
def user_detail(request, user_id):
    # 주어진 user_id로 특정 회원 정보 가져오기 (관리자가 확인하려는 회원)
    user = get_object_or_404(User, id=user_id)

    # 해당 사용자의 교환 내역 조회
    exchange_list = Exchange.objects.filter(user=user).select_related('product')

    # 조회한 정보를 템플릿에 전달
    context = {
        'user': user, # 관리자가 조회하는 회원의 정보
        'exchange_list': exchange_list,  # 해당 회원의 교환 내역
    }

    return render(request, 'manage/user_detail.html', context)




### 교환 신청한 회원 확인 ##############################
def reg_gift(request):
    all_exchange_list = Exchange.objects.select_related('user', 'product').all()
    context = {
        'exchange_list': all_exchange_list,
    }
    return render(request, 'manage/reg_gift.html', context)

### 교환 신청 후 상품 수량 체크
def update_product_change(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        change_cnt = int(request.POST.get('change_cnt'))

        product = get_object_or_404(id=product_id)

        product.product_change += change_cnt
        product.save()

        return redirect('교환신청')
    
# 교환 신청한 회원에게 배송 보내기 완료
def delivery_complete(request, exchange_id):
    exchange = get_object_or_404(Exchange, id=exchange_id) # 기계 객체 가져오기
    exchange.change_dt = timezone.now() # 배달 완료 시간을 현재 시간으로 설정
    exchange.save() # 변경사항 저장

    return redirect('교환신청내역')  # 회원 상세 정보로 리디렉션

##############################

# 상품 관리
def product(request):
    product = Product.objects.all()
    return render(request, 'manage/product.html', {'products':product})

# 상품 등록
def product_upload(request):
    if request.method == 'POST':
        # POST 요청에서 데이터 가져오기
        product_name = request.POST.get('product_name')
        product_point = request.POST.get('product_point')
        product_pet = request.POST.get('product_pet')
        image = request.POST.get('image')  # 이미지 URL

        # Product 객체 생성 및 저장
        product = Product(
            product_name=product_name,
            product_point=product_point,
            product_pet=product_pet,
            image=image,
            product_change=0  # 초기 교환 수
        )
        product.save()
        
        return redirect('상품정보')  # 상품 목록 페이지로 리디렉션 (원하는 URL로 수정)

    return render(request, 'manage/product_upload.html')

# 상품 삭제
def product_delete(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()# 기계 객체 가져오기

    return redirect('상품정보')  # 회원 목록 페이지로 리디렉션

# 상품 수정
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.product_point = request.POST.get('product_point')
        product.product_pet = request.POST.get('product_pet')
        product.image = request.POST.get('image')
        product.save()
        return redirect('상품정보')  # 수정 후 상품 목록 페이지로 리디렉션

    return render(request, 'manage/product_edit.html', {'product': product})



