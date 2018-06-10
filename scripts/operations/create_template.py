import os
def run(context):
    context.parser.add_argument("template_name", help="Template name")
    args = context.parser.parse_args()
    template_name = args.template_name
    
    path1 = "nanotask/templates/{}".format(context.project_name)
    if directory_exists(path1):
        create_file("{}/{}.html".format(path1,template_name),template_body)

    path2 = "scripts/nanotask_csv/{}".format(context.project_name)
    if directory_exists(path2):
        create_file("{}/{}.csv".format(path2,template_name),csv_body)

def directory_exists(dirpath):
    if os.path.exists(dirpath):
        return True
    else:
        print("ERROR: project directory {} does not exist.".format(dirpath))
        return False

def create_file(filepath,body=None):
    if not os.path.exists(filepath):
        f = open(filepath,"a")
        if body:
            f.write(body)
        f.close()
        return True
    else:
        print("CAUTION: skipped creating file {} because it already exists.".format(filepath))
        return False

template_body = '''<style>
    #passed_time_box { border: 2px solid #f00; background: #fdd; width: 30%; font-weight: bold; margin: 10px; padding: 5px; font-size:1.5em; }
    #wrapper { width: 95%; margin: 0 auto; }
    .media_data {
        float: left;
        width: 45%;
        box-sizing: border-box;
        height:240px;
        border: 2px solid #999;
        padding: 10px;
        background: #ddd;
        background-image: url('https://www.mygreatlakes.org/mglstatic/educate/images/loading.gif');
        background-position: center center;
        background-size: auto 20%;
        background-repeat: no-repeat;
    }
    .media_data img { height:100%; max-width:100%; }
    #arrow { float:   left; width: 10%; height: 240px; padding: 50px 10px 0 10px; box-sizing: border-box; font-size: 2.0em; }
    #btns-wrapper { width: 80%; margin: 0 auto; }
    .btn-wrapper { width: 25%; padding: 10px 30px; box-sizing: border-box; float: left; margin-top: 30px; }
    .btn-wrapper button {
        width: 100%;
        box-sizing: border-box;
        padding: 10px;
        font-size: 1.3em;
        color: #fff;
        font-weight: bold;
        cursor: pointer;
        -moz-user-select: none;
        -khtml-user-select: none;
        -webkit-user-select: none;
    }
    .btn-wrapper div:hover { opacity: 0.7; }
    #answer_0 { background: #090; }
    #answer_1 { background: #7e7; }
    #answer_2 { background: #fbb; }
    #answer_3 { background: #c00; }
    .nano-submit[disabled=true] { background: #ccc !important; cursor: default !important; }
    .clear { clear: both; }
</style>

<center>

    <h3>Please answer whether the two images represent the same object.</h3>
    
    <div id="wrapper">
        <div class="media_data"><img src="{{ img_url0 }}" /></div>
        <div id="arrow"> <-> </div>
        <div class="media_data"><img src="{{ img_url1 }}" /></div>
        <div class="clear"></div>
        
        <div id="btns-wrapper">
            <div class="btn-wrapper">
                <button id="answer_0" class="nano-submit" name="choice" value="{{ btn_lbl0 }}">{{ btn_lbl0 }}</button>
            </div>
            <div class="btn-wrapper">
                <button id="answer_1" class="nano-submit" name="choice" value="{{ btn_lbl1 }}">{{ btn_lbl1 }}</button>
            </div>
            <div class="btn-wrapper">
                <button id="answer_2" class="nano-submit" name="choice" value="{{ btn_lbl2 }}">{{ btn_lbl2 }}</button>
            </div>
            <div class="btn-wrapper">
                <button id="answer_3" class="nano-submit" name="choice" value="{{ btn_lbl3 }}">{{ btn_lbl3 }}</button>
            </div>
            <p class="clear"></p>
        </div>
    </div>
</center>

<!--
If a choice is just a multiple-choice question using several buttons, put the same "name" attribute to all buttons with values, with their class names all "nano-submit".
If there are other answer inputs, create hidden input tags with "nano-answer" for class, a key string for name, and a value string for value.
-->

'''

csv_body = ''''img_url0','img_url1','btn_lbl0','btn_lbl1','btn_lbl2','btn_lbl3'
'https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_80%2Cw_300/MTQxNzI4NTg2OTU1NDk5MDE3/donald_trump_photo_michael_stewartwireimage_gettyimages_169093538_croppedjpg.jpg','https://assets.bwbx.io/images/users/iqjWHBFdfxIU/i6t9SMUwKRHk/v0/800x-1.jpg','Same','Maybe Same','Maybe Not Same','Not Same'
'https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_80%2Cw_300/MTQxNzI4NTg2OTU1NDk5MDE3/donald_trump_photo_michael_stewartwireimage_gettyimages_169093538_croppedjpg.jpg','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4mHfYHQutrU7_37FoayDt__u-PxbqkboKcjaW6-sPVU10soFCqw','Same','Maybe Same','Maybe Not Same','Not Same'
'https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_80%2Cw_300/MTQxNzI4NTg2OTU1NDk5MDE3/donald_trump_photo_michael_stewartwireimage_gettyimages_169093538_croppedjpg.jpg','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyjxmaAPZL2EiQ-2rFPBg4UvCCD9YVMUVepP9jX8NPM0WUPZ4Jiw','Same','Maybe Same','Maybe Not Same','Not Same'
'https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_80%2Cw_300/MTQxNzI4NTg2OTU1NDk5MDE3/donald_trump_photo_michael_stewartwireimage_gettyimages_169093538_croppedjpg.jpg','http://www.sponichi.co.jp/entertainment/news/2017/01/22/jpeg/20170121s00041000310000p_view.jpg','Same','Maybe Same','Maybe Not Same','Not Same'
'https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_80%2Cw_300/MTQxNzI4NTg2OTU1NDk5MDE3/donald_trump_photo_michael_stewartwireimage_gettyimages_169093538_croppedjpg.jpg','https://item-shopping.c.yimg.jp/i/j/arune_j-5401','Same','Maybe Same','Maybe Not Same','Not Same'
'http://darenogare-akemi.c.blog.so-net.ne.jp/_images/blog/_a8b/darenogare-akemi/0-3d351.PNG','http://1noce.com/wp-content/uploads/2016/11/pikotarou1-678x381.jpg','Same','Maybe Same','Maybe Not Same','Not Same'
'http://darenogare-akemi.c.blog.so-net.ne.jp/_images/blog/_a8b/darenogare-akemi/0-3d351.PNG','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSRyD7nol_g5gbjs0RsalDp6tvcbT1qb94RKWfTLSEJ0BlvypJm','Same','Maybe Same','Maybe Not Same','Not Same'
'http://darenogare-akemi.c.blog.so-net.ne.jp/_images/blog/_a8b/darenogare-akemi/0-3d351.PNG','http://masakichi0628.c.blog.so-net.ne.jp/_images/blog/_c78/masakichi0628/160929_E58FA4E59D82E5A4A7E9AD94E78E8B.jpg','Same','Maybe Same','Maybe Not Same','Not Same'
'http://darenogare-akemi.c.blog.so-net.ne.jp/_images/blog/_a8b/darenogare-akemi/0-3d351.PNG','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT19q2pAQEQB7PBI7r1Kp1YRj0fMHvI0fWPWwszuBVJNjIZzeP_','Same','Maybe Same','Maybe Not Same','Not Same'
'http://darenogare-akemi.c.blog.so-net.ne.jp/_images/blog/_a8b/darenogare-akemi/0-3d351.PNG','http://dews365.com/wp-content/uploads/2016/10/8545500dd352d74f881560582e47e316.jpg','Same','Maybe Same','Maybe Not Same','Not Same'
'http://anime-tosidensetu.com/wp-content/uploads/2014/12/SnapCrab_NoName_2014-12-3_22-45-20_No-00.jpg','https://www.plazastyle.com/images/charapla-wally/main_img03.png','Same','Maybe Same','Maybe Not Same','Not Same'
'http://anime-tosidensetu.com/wp-content/uploads/2014/12/SnapCrab_NoName_2014-12-3_22-45-20_No-00.jpg','https://obs.line-scdn.net/0h8KIxRVq0Z2R0AUi2TEwYMzlcYQsNYn1sHnlwXgFXbUoBbXBkHHtwQAhZYQwBLSRnThB3STF-ailaSH9NFQ9Mazl-MQo5SXtVCQNhRCFqJVRdMCQzTWEhAFQBMQFYMSczTCIpBQYBPQZYYQ/small','Same','Maybe Same','Maybe Not Same','Not Same'
'http://anime-tosidensetu.com/wp-content/uploads/2014/12/SnapCrab_NoName_2014-12-3_22-45-20_No-00.jpg','https://rr.img.naver.jp/mig?src=http%3A%2F%2Fimgcc.naver.jp%2Fkaze%2Fmission%2FUSER%2F20121013%2F10%2F1183800%2F160%2F640x960x639501ba53d47e1b682ce7f7.jpg%2F300%2F600&twidth=300&theight=600&qlt=80&res_format=jpg&op=r','Same','Maybe Same','Maybe Not Same','Not Same'
'http://anime-tosidensetu.com/wp-content/uploads/2014/12/SnapCrab_NoName_2014-12-3_22-45-20_No-00.jpg','http://img01.miyachan.cc/usr/piace/20110712_001.jpg','Same','Maybe Same','Maybe Not Same','Not Same'
'http://anime-tosidensetu.com/wp-content/uploads/2014/12/SnapCrab_NoName_2014-12-3_22-45-20_No-00.jpg','https://obs.line-scdn.net/0h4vWukrPZa1lqDESDQ1kUDidRbTYTb3FRAHR8Yx9aYXcfYHxZAnZ8fRZUbTEfIH9yPmkgWBxTUG4HYVtaEyl6VDANbi5HQE8OMBdlSgx8KWlDPSgLUWwiOk8MPTxGPC8JUy8lOBgEMDkQPw/small','Same','Maybe Same','Maybe Not Same','Not Same'
'''
