var lecture_search_list = [];
var lecture_view_list = [];
var lecture_timetable_generator_list = [];
var lecture_timetable_generator_results = [];
var lecture_timetable_generator_results_index = 0;
var mouseover_lecture = null;

var lecture_color_list = [ '#ef5350', '#ab47bc', '#ec407a', '#ec407a', '#2196f3', '#43a047', '#827717', '#ef6c00'];
class Lecture
{
    private data;
    constructor(data) {
        this.data = data;
    }

    public get_data(name) {
        return this.data[name];
    }
}

function convert_time_data(time_data) {
    var w = Math.floor(time_data.start_time/86400);
    var stime = time_data.start_time - w*86400 - 9*3600;
    var etime = time_data.end_time - w*86400 - 9*3600;

    var start_i = Math.ceil(stime/1800);
    var end_i = Math.ceil(etime/1800);

    if(start_i < 0) start_i = 0;
    if(end_i > 23) end_i = 23;

    return {
        weekday: w,
        start: start_i,
        end: end_i
    }
}

function get_lecture(code) {
    for(var i=0; i<lecture_search_list.length; i++) {
        if(lecture_search_list[i].get_data('code') == code) return lecture_search_list[i];
    }
    for(var i=0; i<lecture_view_list.length; i++) {
        if(lecture_view_list[i].get_data('code') == code) return lecture_view_list[i];
    }
    for(var i=0; i<lecture_timetable_generator_list.length; i++) {
        if(lecture_timetable_generator_list[i].get_data('code') == code) return lecture_timetable_generator_list[i];
    }
    return null;
}

function update_lecture_view_list(table_only) {
    if(!table_only) {
        var html = '';
        for(var i=0; i<lecture_view_list.length; i++) {
            var lecture = lecture_view_list[i];
            html += "<li class=\"list-group-item\"><a href=\"javascript:void(0)\" onclick=\"lecture_view_onclick('" + lecture.get_data('code') +"')\" onmouseover=\"lecture_onmouseover('" + lecture.get_data('code') +"')\"  onmouseout=\"lecture_onmouseout('" + lecture.get_data('code') +"')\"><h4>" + lecture.get_data('subject_name') + '</h4><p>' + lecture.get_data('code') + '</p></a></li>';
        }

        $('#lecture_view_list').html(html);
    }

    clearTimetable();

    for(var i=0;i < lecture_view_list.length;i++) {
        var lecture = lecture_view_list[i];
        var lecture_time = lecture.get_data('timetable');
        for (var j = 0 ; j < lecture_time.length ; j++ ) {
            var time_info = convert_time_data(lecture_time[j]);

            var weekday = 'mon';
            if (time_info['weekday'] == 0) weekday = 'mon';
            else if (time_info['weekday'] == 1) weekday = 'tue';
            else if (time_info['weekday'] == 2) weekday = 'wed';
            else if (time_info['weekday'] == 3) weekday = 'thu';
            else if (time_info['weekday'] == 4) weekday = 'fri';
            else if (time_info['weekday'] == 5) weekday = 'sat';

            for(var t=time_info['start']; t< time_info['end']; t++) {
                $('#'+weekday+'_'+(t+1)).css('background-color', lecture_color_list[i]);
            }

            /* $('#'+weekday+'_'+time_info['start']).html(
                 "<a class=\"list-group-item\" href=\"#\" onclick=\"lecture_view_onclick('" + lecture.get_data('code') +"')\" onmouseover=\"lecture_onmouseover('" + lecture.get_data('code') +"')\"><h4>" + lecture.get_data('subject_name') + '</h4><p>' + lecture.get_data('code') + '</p></a>'
            );*/
            $('#'+weekday+'_'+(time_info.start + 1)).html(
                '<div class="lecture-timetable-overlay"><a href="javascript:void(0)" onclick="lecture_view_onclick(\'' + lecture.get_data('code') + '\')" onmouseover="lecture_onmouseover(\'' + lecture.get_data('code') + '\')" onmouseout="lecture_onmouseout(\'' + lecture.get_data('code') + '\')" >' + lecture.get_data('subject_name') + '<br>' + lecture.get_data('code') + '</a></div>'
            );



            //$('#'+weekday+'_'+time_info['end'].toString()).css('background-color', 'yellow');
        }
    }

    if(mouseover_lecture != null) {
        for(var i=0;i < lecture_view_list.length;i++) {
            if(lecture_view_list[i].get_data('code') == mouseover_lecture.get_data('code')) return;
        }

        var lecture = mouseover_lecture;

        var lecture_time = lecture.get_data('timetable');
        for (var j = 0 ; j < lecture_time.length ; j++ ) {
            var time_info = convert_time_data(lecture_time[j]);

            var weekday = 'mon';
            if (time_info['weekday'] == 0) weekday = 'mon';
            else if (time_info['weekday'] == 1) weekday = 'tue';
            else if (time_info['weekday'] == 2) weekday = 'wed';
            else if (time_info['weekday'] == 3) weekday = 'thu';
            else if (time_info['weekday'] == 4) weekday = 'fri';
            else if (time_info['weekday'] == 5) weekday = 'sat';

            for(var t=time_info['start']; t<time_info['end']; t++) {
                $('#'+weekday+'_'+(t+1)).css('background-color', lecture_color_list[i]);
            }

            /* $('#'+weekday+'_'+time_info['start']).html(
                 "<a class=\"list-group-item\" href=\"#\" onclick=\"lecture_view_onclick('" + lecture.get_data('code') +"')\" onmouseover=\"lecture_onmouseover('" + lecture.get_data('code') +"')\"><h4>" + lecture.get_data('subject_name') + '</h4><p>' + lecture.get_data('code') + '</p></a>'
            );*/
            $('#'+weekday+'_'+(time_info.start+1)).html(
                '<div class="lecture-timetable-overlay"><a href="javascript:void(0)" onclick="lecture_view_onclick(\'' + lecture.get_data('code') + '\')" onmouseover="lecture_onmouseover(\'' + lecture.get_data('code') + '\')" onmouseout="lecture_onmouseout(\'' + lecture.get_data('code') + '\')" >' + lecture.get_data('subject_name') + '<br>' + lecture.get_data('code') + '</a></div>'
            );

            //$('#'+weekday+'_'+time_info['end'].toString()).css('background-color', 'yellow');
        }
    }
}

function update_lecture_timetable_generator_list() {
    var html='';
    for(var i=0; i<lecture_timetable_generator_list.length; i++) {
        var lecture = lecture_timetable_generator_list[i];
        html += "<a class=\"list-group-item\" href=\"#\" onclick=\"lecture_timetable_generator_list_onclick('" + lecture.get_data('code') +"')\" onmouseover=\"lecture_onmouseover('" + lecture.get_data('code') +"')\" onmouseout=\"lecture_onmouseout('" + lecture.get_data('code') +"')\"><h4>" + lecture.get_data('subject_name') + '</h4><p>' + lecture.get_data('code') + '</p></a>';
    }

    $('#lecture_timetable_generator_lecture_list').html(html);
}

function lecture_timetable_generator_list_onclick(code) {
    for(var i=0; i<lecture_timetable_generator_list.length; i++) {
        if(lecture_timetable_generator_list[i].get_data('code') == code) {
            lecture_timetable_generator_list.splice(i, 1);
            update_lecture_timetable_generator_list();
            return;
        }
    }
}

function lecture_view_onclick(code) {
    for(var i=0; i<lecture_view_list.length; i++) {
        if(lecture_view_list[i].get_data('code') == code) {
            lecture_view_list.splice(i, 1);
            update_lecture_view_list(false);
            return;
        }
    }
}

function get_weekday(time) {
    if(time < 60*60*24) return '월';
    if(time < 60*60*24*2) return '화';
    if(time < 60*60*24*3) return '수';
    if(time < 60*60*24*4) return '목';
    if(time < 60*60*24*5) return '금';
    if(time < 60*60*24*6) return '토';
     return '일';
}

function get_time_text(time) {
    time = time - Math.floor(time/86400) * 86400;

    var h = Math.floor(time / 3600);
    var m = time - h*3600;
    m = m /60;
    return ("0" + h).slice(-2) + ':' + ("0" + m).slice(-2);
}

function detail_lecture_info(lecture) {
    if(lecture == null) {
        $('.class-detail-view').hide();
        return;
    }

    $('#detail_lecture_info_subject_name').html(lecture.get_data('subject_name'));
    $('#detail_lecture_info_code').html(lecture.get_data('code'));
    $('#detail_lecture_info_professors').html(lecture.get_data('professors'));
    $('#detail_lecture_info_departments').html(lecture.get_data('departments'));
    $('#detail_lecture_info_type').html(lecture.get_data('type'));
    $('#detail_lecture_info_credit').html(lecture.get_data('credit') + '학점');
    if(lecture.get_data('tags')=='') {
        $('#detail_lecture_info_tags').hide();
    } else {
        $('#detail_lecture_info_tags').show();
    }
    $('#detail_lecture_info_tags').html(lecture.get_data('tags'));

    var timetable_html = '';
    var timetable = lecture.get_data('timetable');
    for(var i=0; i<timetable.length; i++) {
        var time_data = timetable[i];
        timetable_html += "<div class=\"well\" onmouseover=\"update_map('" + time_data.place + "')\"><p>" + get_weekday(time_data.start_time) + '요일 ' + get_time_text(time_data.start_time) + ' ~ ' + get_time_text(time_data.end_time) + '</p><p>' + time_data.place + time_data.room + '</p></div>';
    }

    $('#detail_lecture_info_timetable').html(timetable_html);

    if(timetable.length > 0) {
        update_map(timetable[0].place);
    }

    $('.class-detail-view').show();
}

function lecture_onmouseover(code) {
    var lecture = get_lecture(code);
    detail_lecture_info(lecture);

    mouseover_lecture = lecture;
    update_lecture_view_list(true);
}

function lecture_onmouseout(code) {
    //var lecture = get_lecture(code);
    //detail_lecture_info(null);

    mouseover_lecture = null;
    update_lecture_view_list(false);
}

function search_result_onclick(code) {
    var lecture = get_lecture(code);

    if($("#create_timetable_box").is(":visible")) {
        for(var i=0; i<lecture_timetable_generator_list.length; i++) {
            if(lecture_timetable_generator_list[i].get_data('code') == lecture.get_data('code')) {
                alert('이미 추가되어있는 강의입니다.');
                return;
            }
        }
        lecture_timetable_generator_list.push(lecture);
        update_lecture_timetable_generator_list();
        return;
    }

    for(var i=0; i<lecture_view_list.length; i++) {
        if(lecture_view_list[i].get_data('subject_code') == lecture.get_data('subject_code')) {
            alert('이미 추가되어있는 강의입니다.');
            return;
        }
    }
    lecture_view_list.push(lecture);
    update_lecture_view_list();
}

function init() {
    $('#vtimetable_search').submit(function() {
        var year = $('#select_year').val();
        var term = $('#select_semester').val();
        var query = $('#select_query').val();

        $.get('/lectures/vtimetable/search?year='+year+'&term='+term+'&q='+encodeURIComponent(query), function(result){
            var view = $('#search_results');
            var data = "";
            lecture_search_list.length = 0;
            for(var i=0; i<result.data.length; i++) {
                var lecture = new Lecture(result.data[i]);
                lecture_search_list.push(lecture);
                data = data + "<a class=\"list-group-item\" href=\"#\" onclick=\"search_result_onclick('" + lecture.get_data('code') +"')\" onmouseover=\"lecture_onmouseover('" + lecture.get_data('code') +"')\" onmouseout=\"lecture_onmouseout('" + lecture.get_data('code') +"')\"><h4>" + lecture.get_data('subject_name') + '</h4><p>' + lecture.get_data('code') + '</p></a>';
            }
            view.html(data);
        });

        return false;
    });

    $('#toggle_create_btn').click(function () {
        $('#create_timetable_box').slideToggle();
    });

    $('.timetable').mousedown(function () {
        $.bind('mousemove', selectCells);
        $.bind('mouseup', resetAllCells);
    });

    var selectCells = function (event) {
        console.log(event);
    };

    var resetAllCells = function (event) {
        console.log(event);
    };

    $('#timetable_generator_generate_btn').click(generate_timetable);
    $('#timetable_generator_pre_btn').click(timetable_generator_pre_btn_click);
    $('#timetable_generator_next_btn').click(timetable_generator_next_btn_click);

    detail_lecture_info(null);
}

function generate_timetable() {
    try {
        var min_credit = Number($('#timetable_generator_min_credit').val());
        var max_credit = Number($('#timetable_generator_max_credit').val());
    } catch(e) {
        alert("최소, 최대 학점을 올바로 입력하여 주십시오.");
        return;
    }

    lecture_timetable_generator_results.length = 0;
    lecture_timetable_generator_results_index = -1;
    var lecture_merge_obj = {};
    for(var i=0; i<lecture_timetable_generator_list.length; i++) {
        var lecture = lecture_timetable_generator_list[i];
        var subject_code = lecture.get_data('subject_code');
        if(subject_code in lecture_merge_obj) {
            lecture_merge_obj[subject_code].push(lecture);
        } else {
            lecture_merge_obj[subject_code] = [lecture];
        }
    }

    var lecture_merge_obj_list = $.map(lecture_merge_obj, function(value, index) {
        return [value];
    });


    function push_timetable(arr){
        var timetable = [];
        for(var timetable_i=0; timetable_i<7; timetable_i++) {
            var temp = [];
            for(var t=0; t<24; t++) {
                temp.push(false);
            }
            timetable.push(temp);
        }

        var credit = 0;
        for(var arr_i=0; arr_i<arr.length; arr_i++) {
            credit += arr[arr_i].get_data('credit');

            for(var i=0; i<arr[arr_i].get_data('timetable').length; i++) {
                var time = convert_time_data(arr[arr_i].get_data('timetable')[i]);

                for (var timetable_i = time.start; timetable_i < time.end; timetable_i++) {
                    if(timetable[time.weekday][timetable_i]) return;
                    timetable[time.weekday][timetable_i] = true;
                }
            }
        }

        if(min_credit > credit) return;
        if(max_credit < credit) return;

        lecture_timetable_generator_results.push(arr);
    }

    function generate_timetable_lectures(arr, ind) {
        if(ind>=arr.length) {
            push_timetable(arr);
            return;
        }

        for(var i=0; i<arr[ind].length; i++) {
            var clone = arr.slice(0);
            clone[ind] = arr[ind][i];
            generate_timetable_lectures(clone, ind+1);
        }
    }

    function generate_timetable_arr(n, ind, arr) {
        arr.push(ind);

        if(n == 1) {
            for(var arr_i=0; arr_i<arr.length; arr_i++) {
                arr[arr_i] = lecture_merge_obj_list[arr[arr_i]];
            }
            generate_timetable_lectures(arr, 0);
            return;
        }

        for(var i=ind+1; i<lecture_merge_obj_list.length; i++) {
            generate_timetable_arr(n-1, i, arr.slice(0));
        }
    }

    for(var n_i=1; n_i<=lecture_merge_obj_list.length; n_i++) {
        for (var start_i = 0; start_i < lecture_merge_obj_list.length; start_i++) {
            generate_timetable_arr(n_i, start_i, []);
        }
    }

    timetable_generator_next_btn_click();
}

function timetable_generator_pre_btn_click() {
    lecture_timetable_generator_results_index -= 1;
    if(lecture_timetable_generator_results_index < 0) {
        lecture_timetable_generator_results_index = 0;
    }

    if(lecture_timetable_generator_results.length < 1 || lecture_timetable_generator_results_index > lecture_timetable_generator_results.length) {
        alert('존재하지 않습니다');
        return;
    }

    var lectures = lecture_timetable_generator_results[lecture_timetable_generator_results_index];
    lecture_view_list = lectures.slice(0);
    update_lecture_view_list();

    $('#timetable_generator_generate_btn').html((lecture_timetable_generator_results_index+1) + '/' + lecture_timetable_generator_results.length);
}

function timetable_generator_next_btn_click() {
    lecture_timetable_generator_results_index += 1;
    if(lecture_timetable_generator_results_index >= lecture_timetable_generator_results.length) {
        lecture_timetable_generator_results_index = lecture_timetable_generator_results.length - 1;
    }
    if(lecture_timetable_generator_results_index < 0) {
        lecture_timetable_generator_results_index = 0;
    }

    if(lecture_timetable_generator_results.length < 1 || lecture_timetable_generator_results_index > lecture_timetable_generator_results.length) {
        alert('존재하지 않습니다');
        return;
    }

    var lectures = lecture_timetable_generator_results[lecture_timetable_generator_results_index];
    lecture_view_list = lectures.slice(0);
    update_lecture_view_list();

    $('#timetable_generator_generate_btn').html((lecture_timetable_generator_results_index+1) + '/' + lecture_timetable_generator_results.length);
}
function clearTimetable () {
    for (var i = 1 ; i <= 6 ; i++ ) {
        var weekday = 'mon';
        if ( i == 1 ) weekday = 'mon';
        else if ( i == 2 ) weekday = 'tue';
        else if ( i == 3 ) weekday = 'wed';
        else if ( i == 4 ) weekday = 'thu';
        else if ( i == 5 ) weekday = 'fri';
        else if ( i == 6 ) weekday = 'sat';

        for ( var j = 1 ; j <= 24 ; j++ ) {
            $('#'+ weekday + '_' + j).css('background-color', '');
            $('#'+ weekday + '_' + j).html('');
        }
    }
}

$(function () {
    init();
});

$(function () {
    var period_table = {
        1: '09:00',
        2: '09:30',
        3: '10:00',
        4: '10:30',
        5: '11:00',
        6: '11:30',
        7: '12:00',
        8: '12:30',
        9: '13:00',
        10: '13:30',
        11: '14:00',
        12: '14:30',
        13: '15:00',
        14: '15:30',
        15: '16:00',
        16: '16:30',
        17: '17:00',
        18: '17:30',
        19: '18:00',
        20: '18:30',
        21: '19:00',
        22: '19:30',
        23: '20:00',
        24: '20:30'
    }
    for (var time = 1; time <= 24; time++) {
        var time_string = period_table[time];
        $('.timetable').append(
            '<div class="row"> \
                <div class="cell-time"> \
                    <p>' + time_string + '</p> \
                </div> \
                <div id="' + 'mon_' + time + '" class="cell"> \
                </div> \
                <div id="' + 'tue_' + time + '" class="cell"> \
                </div> \
                <div id="' + 'wed_' + time + '" class="cell"> \
                </div> \
                <div id="' + 'thu_' + time + '" class="cell"> \
                </div> \
                <div id="' + 'fri_' + time + '" class="cell"> \
                </div>\
                <div id="' + 'sat_' + time + '" class="cell">\
                </div>\
            </div>'
        );

    }
});