(function($) {
'use strict';


$("#navbar-form-sign-up").submit(function(e) {
    e.preventDefault();

    $("small[id$='-err']").text('');

    const $login = $(this).find('input[name="login"]');
    const $email = $(this).find('input[name="email"]');
    const $name = $(this).find('input[name="name"]');
    const $surname = $(this).find('input[name="surname"]');
    const $gender = $(this).find('select[name="gender"]');
    const $pwd = $(this).find('input[name="pwd"]');
    const $pwdConfirm = $(this).find('input[name="pwd-confirm"]');

    let errors = {};

    if ($login.val().length < 3) {
        errors['login'] = 'Login is too short! Min length - 3 characters!';
    } else if (!$login.hasClass('border-success')) {
        errors['login'] = 'Login is already taken!';
    }

    if (!/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test($email.val().toLowerCase())) {
        errors['email'] = 'Invalid email format!';
    } else if (!$email.hasClass('border-success')) {
        errors['login'] = 'Email is already taken!';
    }

    if ($name.val().length > 0 && !/^[a-zа-я]{2,}$/.test($name.val().toLowerCase())) {
        errors['name'] = 'Name is invalid!';
    }
    if ($surname.val().length > 0 && !/^[a-zа-я]{2,}$/.test($surname.val().toLowerCase())) {
        errors['surname'] = 'Surname is invalid!';
    }

    if ($pwd.val().length < 6) {
        errors['pwd'] = 'Password is too short! Min length - 6 characters';
    }
    if ($pwd.val() !== $pwdConfirm.val()) {
        errors['pwd-confirm'] = 'Passwords do not match!';
    }



    let errorsCount = Object.keys(errors).length;
    console.log("Errors count - " + errorsCount)
    if (errorsCount == 0) {
        $.ajax({
            url: 'http://localhost:5000/sign_up',
            type: 'POST',
            dataType: 'json',
            data: {
                'login': $login.val(),
                'email': $email.val(),
                'name': $name.val(),
                'surname': $surname.val(),
                'gender': $gender.val(),
                'pwd': $pwd.val()
            },
            success: function(json) {
                if (json['status'] == 'OK') {
                    window.location.reload();
                } else {
                    console.warn(json['err_description']);
                }
            }
        });
    }

    for (let key in errors) {
        $('#' + key + '-err').text(errors[key]);
    }

    return false;
});

$("#navbar-form-sign-up input[name='login']").on('blur', function() {
    if ($(this).val().length == 0) {
        $(this).attr('placeholder', 'Login');
        $(this).removeClass('border-success border-error border-warning');
        return;
    }

    checkLogin($(this));
});

$("#navbar-form-sign-up input[name='login']").on('focus', function() {
    $(this).attr('placeholder', 'Min length - 3 characters');
});

$("#navbar-form-sign-up input[name='email']").on('blur', function() {
    if ($(this).val().length == 0) {
        $(this).attr('placeholder', 'Email');
        $(this).removeClass('border-success border-error border-warning');
        return;
    }

    checkEmail($(this));
});

$("#navbar-form-sign-up input[name='email']").on('focus', function() {
    $(this).attr('placeholder', 'Enter valid email address');
});

$("#navbar-form-sign-up input[name='name'], #navbar-form-sign-up input[name='surname']").on('blur', function() {
    if ($(this).val().length == 0) {
        $(this).removeClass('border-warning border-error border-success');
        return;
    }

    const success = /^[a-zа-я]{2,}$/.test($(this).val().toLowerCase());

    if (success) {
        $(this).removeClass('border-warning border-error').addClass('border-success');
    } else {
        $(this).removeClass('border-warning border-error').addClass('border-warning');
    }
});

$("#navbar-form-sign-up input[name='pwd'], #navbar-form-sign-up input[name='pwd-confirm']").on('blur', function() {
    const $pwd = $("#navbar-form-sign-up input[name='pwd']");
    const $pwdConfirm = $("#navbar-form-sign-up input[name='pwd-confirm']");

    if ($pwd.val().length < 6) {
        $pwd.removeClass('border-success border-warning').addClass('border-error');
    } else {
        $pwd.removeClass('border-error border-warning').addClass('border-success');
    }

    if ($pwd.val() === $pwdConfirm.val() && $pwd.hasClass('border-success')) {
        $pwdConfirm.removeClass('border-error border-warning').addClass('border-success');
    } else {
        $pwdConfirm.removeClass('border-success border-warning').addClass('border-error');
    }
});

$("#navbar-form-sign-up input[name='pwd']").on('focus', function() {
    $(this).attr('placeholder', 'Min password length - 6 characters');
});

function checkLogin($login) {
    if ($login.val().length < 3) {
        $login.removeClass('border-success border-error').addClass('border-warning');
        return;
    }

    $.ajax({
        url: 'http://localhost:5000/ajax/check-login',
        type: 'GET',
        dataType: 'json',
        data: {
            'login': $login.val()
        },
        success: function(json) {
            if (json['status'] == 'OK') {
                if (json['login_status'] == 'free') {
                    console.log('login is free');
                    $login.removeClass('border-error border-warning').addClass('border-success');
                } else {
                    console.log('login is taken');
                    $login.removeClass('border-success border-warning').addClass('border-error');
                }
            } else if (json['status'] == 'ERR') {
                console.warn(json['err_description']);
                $login.removeClass('border-success border-error').addClass('border-warning');
            }
        },
        error: function() {
            console.warn("error");
            $login.removeClass('border-success border-error').addClass('border-warning');
        }
    });
}

function checkEmail($email) {
    const valid = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test($email.val().toLowerCase());

    if (!valid) {
        $email.removeClass('border-success border-error').addClass('border-warning');
        return;
    }

    $.ajax({
        url: 'http://localhost:5000/ajax/check-login',
        type: 'GET',
        dataType: 'json',
        data: {
            'login': $email.val()
        },
        success: function(json) {
            if (json['status'] == 'OK') {
                if (json['login_status'] == 'free') {
                    console.log('email is free');
                    $email.removeClass('border-error border-warning').addClass('border-success');
                } else {
                    console.log('email is taken');
                    $email.removeClass('border-success border-warning').addClass('border-error');
                }
            } else if (json['status'] == 'ERR') {
                console.warn(json['err_description']);
                $email.removeClass('border-success border-error').addClass('border-warning');
            }
        },
        error: function() {
            console.warn("error");
            $email.removeClass('border-success border-error').addClass('border-warning');
        }
    });
}

})(jQuery);