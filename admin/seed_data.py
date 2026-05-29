"""Seed default content for Tai Chi lessons, trip packages, teachers, and Chinese courses."""
from extensions import db
from models.tai_chi_lesson import TaiChiLesson
from models.trip_package import TripPackage
from models.teacher import Teacher
from models.chinese_course import ChineseCourse


TAI_CHI_24 = [
    (1, 'Commencing Form', '起势'),
    (2, 'Part the Wild Horse\'s Mane', '左右野马分鬃'),
    (3, 'White Crane Spreads Its Wings', '白鹤亮翅'),
    (4, 'Brush Knee and Push (left & right)', '左右搂膝拗步'),
    (5, 'Playing the Lute', '手挥琵琶'),
    (6, 'Reverse Reeling Forearm', '左右倒卷肱'),
    (7, 'Left Grasp Sparrow\'s Tail', '左揽雀尾'),
    (8, 'Right Grasp Sparrow\'s Tail', '右揽雀尾'),
    (9, 'Single Whip', '单鞭'),
    (10, 'Wave Hands Like Clouds', '云手'),
    (11, 'Single Whip', '单鞭'),
    (12, 'High Pat on Horse', '高探马'),
    (13, 'Right Heel Kick', '右蹬脚'),
    (14, 'Strike Opponent\'s Ears with Both Fists', '双峰贯耳'),
    (15, 'Turn Body and Left Heel Kick', '转身左蹬脚'),
    (16, 'Left Lower Body and Stand on One Leg', '左下势独立'),
    (17, 'Right Lower Body and Stand on One Leg', '右下势独立'),
    (18, 'Shuttle Back and Forth', '左右穿梭'),
    (19, 'Needle at Sea Bottom', '海底针'),
    (20, 'Fan Through Back', '闪通臂'),
    (21, 'Turn Body, Deflect, Parry, and Punch', '转身搬拦捶'),
    (22, 'Apparent Close-Up', '如封似闭'),
    (23, 'Cross Hands', '十字手'),
    (24, 'Closing Form', '收势'),
]


TRIP_PACKAGES = [
    ('101', 'Beijing Imperial Heritage Tour', '北京皇城文化游',
     'Beijing', '北京', 5, 1800, 2800,
     'Culture lovers, first-time visitors', '文化爱好者，首次来华游客',
     'Forbidden City, Great Wall (Mutianyu), Temple of Heaven, traditional Hutong walk'),
    ('102', 'Xi\'an Ancient Capital Tour', '西安古都文化游',
     'Xi\'an', '西安', 4, 1400, 2200,
     'History buffs, photographers', '历史爱好者，摄影爱好者',
     'Terracotta Warriors, City Wall cycling, Tang Dynasty cultural show'),
    ('103', 'Shanghai Modern Metropolis Tour', '上海现代都市游',
     'Shanghai', '上海', 4, 1600, 2600,
     'Cosmopolitan travelers', '都市生活爱好者',
     'The Bund, Lujiazui skyline, Yu Garden, French Concession'),
    ('104', 'Guilin Karst Landscape Tour', '桂林山水游',
     'Guilin', '桂林', 5, 1500, 2400,
     'Nature lovers, photographers', '自然爱好者，摄影爱好者',
     'Li River cruise, Yangshuo cycling, Longji Rice Terraces'),
    ('105', 'Chengdu Panda & Cuisine Tour', '成都熊猫美食游',
     'Chengdu', '成都', 5, 1700, 2800,
     'Families, food lovers', '亲子家庭，美食爱好者',
     'Panda Research Base, Sichuan hotpot, Leshan Giant Buddha'),
    ('106', 'Yunnan Ethnic Cultures Tour', '云南民族风情游',
     'Yunnan', '云南', 7, 2200, 3500,
     'Cultural explorers', '文化探索者',
     'Kunming, Dali Old Town, Lijiang, Shangri-La'),
    ('107', 'Silk Road Discovery Tour', '丝绸之路文化游',
     'Gansu', '甘肃', 8, 2800, 4500,
     'Adventure & history seekers', '历史探险爱好者',
     'Dunhuang Mogao Caves, Crescent Lake, Jiayuguan Fortress'),
    ('108', 'Tibet Sacred Plateau Tour', '西藏圣地游',
     'Tibet', '西藏', 8, 3500, 5500,
     'Spiritual seekers, trekkers', '心灵旅行者，徒步爱好者',
     'Potala Palace, Jokhang Temple, Namtso Lake'),
    ('109', 'Zhangjiajie Natural Wonders Tour', '张家界自然奇观游',
     'Zhangjiajie', '张家界', 5, 1600, 2600,
     'Outdoor & adventure travelers', '户外探险者',
     'Tianmen Mountain, Glass Bridge, Avatar Mountain'),
    ('110', 'Huangshan & Huizhou Culture Tour', '黄山徽州文化游',
     'Huangshan', '黄山', 5, 1700, 2700,
     'Artists, culture & nature lovers', '艺术家、文化与自然爱好者',
     'Yellow Mountain sunrise, Hongcun village, Hui-style cuisine'),
]


SAMPLE_TEACHERS = [
    ('Li Wei', '李伟', 'Mandarin & Pinyin (Adult)', '成人中文与拼音',
     '8 years', '8年', 'Mandarin, English, French'),
    ('Zhang Min', '张敏', 'Children\'s Chinese & Conversation', '儿童中文与会话',
     '6 years', '6年', 'Mandarin, English'),
    ('Wang Hong', '王红', 'Business Chinese & HSK Prep', '商务中文与HSK备考',
     '10 years', '10年', 'Mandarin, English, German'),
]


SAMPLE_CHINESE_COURSES = [
    ('Kids Mandarin (Ages 5-12)', '少儿中文（5-12岁）', 'kids',
     'Fun, immersive lessons covering Pinyin, characters, songs, and stories.',
     '寓教于乐，覆盖拼音、汉字、儿歌和故事。', 240),
    ('Adult Beginner Mandarin', '成人零基础中文', 'adult',
     'Structured 12-week course from Pinyin to everyday conversation.',
     '12周体系化课程，从拼音到日常会话。', 360),
    ('Pinyin Crash Course', '拼音速成班', 'pinyin',
     '4-week intensive on tones, finals, and pronunciation.',
     '4周强化训练，掌握声调、韵母与发音。', 120),
    ('Conversation Practice', '会话练习', 'conversation',
     'Weekly 1-on-1 speaking sessions with native teachers.',
     '每周一对一口语训练，母语教师指导。', 200),
    ('Business Mandarin', '商务中文', 'business',
     'Professional vocabulary, meetings, emails, and negotiations.',
     '商务词汇、会议、邮件与谈判。', 480),
]


def seed_tai_chi():
    count = 0
    for number, en, zh in TAI_CHI_24:
        if TaiChiLesson.query.filter_by(number=number).first():
            continue
        lesson = TaiChiLesson(
            number=number,
            name_en=en,
            name_zh=zh,
            is_free=(number <= 2),
            is_active=True,
        )
        db.session.add(lesson)
        count += 1
    db.session.commit()
    return count


def seed_trips():
    count = 0
    for row in TRIP_PACKAGES:
        code, title_en, title_zh, dest_en, dest_zh, days, pmin, pmax, aud_en, aud_zh, highlights = row
        if TripPackage.query.filter_by(code=code).first():
            continue
        pkg = TripPackage(
            code=code, title_en=title_en, title_zh=title_zh,
            destination_en=dest_en, destination_zh=dest_zh,
            days=days, price_min=pmin, price_max=pmax,
            audience_en=aud_en, audience_zh=aud_zh,
            highlights_en=highlights, highlights_zh=highlights,
            sort_order=int(code), is_active=True,
        )
        db.session.add(pkg)
        count += 1
    db.session.commit()
    return count


def seed_teachers():
    count = 0
    for i, (en, zh, spec_en, spec_zh, exp_en, exp_zh, langs) in enumerate(SAMPLE_TEACHERS):
        if Teacher.query.filter_by(name_en=en).first():
            continue
        t = Teacher(
            name_en=en, name_zh=zh,
            specialty_en=spec_en, specialty_zh=spec_zh,
            experience_en=exp_en, experience_zh=exp_zh,
            languages=langs, sort_order=i, is_active=True,
        )
        db.session.add(t)
        count += 1
    db.session.commit()
    return count


def seed_chinese_courses():
    count = 0
    for i, (en, zh, cat, desc_en, desc_zh, price) in enumerate(SAMPLE_CHINESE_COURSES):
        if ChineseCourse.query.filter_by(name_en=en).first():
            continue
        c = ChineseCourse(
            name_en=en, name_zh=zh, category=cat,
            description_en=desc_en, description_zh=desc_zh,
            price=price, sort_order=i, is_active=True,
        )
        db.session.add(c)
        count += 1
    db.session.commit()
    return count
