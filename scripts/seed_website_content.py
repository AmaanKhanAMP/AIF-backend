"""Seed CMS tables with the public website's current hardcoded content.

Safe to run multiple times:
- Matches existing rows by stable keys (title / name + resource)
- Updates fields when a match is found
- Inserts when missing
- Never creates duplicates

Usage (from backend/ with venv active):
  python scripts/seed_website_content.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.cms_models import (
    FeaturedEvent,
    FooterFocusItem,
    FooterLink,
    FooterSettings,
    GalleryItem,
    HeroBanner,
    HomeEvent,
    HomeGalleryItem,
    HomeProject,
    NavbarItem,
    NavbarSettings,
    Testimonial,
    UpcomingEvent,
    utcnow,
)

# ── Content extracted from frontend/components (canonical App Router) ─────────

HERO_BANNERS = [
    {
        "title": "Empowering Youth Through",
        "title_accent": "Education",
        "subtitle": (
            "Every brilliant mind deserves an opportunity. We build impactful "
            "educational paths to secure sustainable futures for underprivileged students."
        ),
        "image_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1920&q=80",
        "primary_btn_text": "READ MORE",
        "primary_btn_link": "/about",
        "secondary_btn_text": "OUR PROJECTS",
        "secondary_btn_link": "/projects",
        "display_order": 1,
    },
    {
        "title": "Bridging the Gap to Rightful",
        "title_accent": "Employment",
        "subtitle": (
            "Transforming potential into professions. Our structured training modules "
            "open direct job avenues for deserving job seekers."
        ),
        "image_url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?auto=format&fit=crop&w=1920&q=80",
        "primary_btn_text": "JOIN US",
        "primary_btn_link": "/volunteer",
        "secondary_btn_text": "VIEW IMPACT",
        "secondary_btn_link": "/about",
        "display_order": 2,
    },
    {
        "title": "Sustaining Growth via Economic",
        "title_accent": "Empowerment",
        "subtitle": (
            "Uplifting grassroots communities by fostering self-reliance, practical "
            "skill development setups, and small-scale business incubation."
        ),
        "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=1920&q=80",
        "primary_btn_text": "SUPPORT US",
        "primary_btn_link": "/support-us",
        "secondary_btn_text": "OUR MISSION",
        "secondary_btn_link": "/what-we-do",
        "display_order": 3,
    },
]

HOME_PROJECTS = [
    {
        "title": "ACE - Academy for Competitive Exams",
        "image_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=600&q=80",
        "display_order": 1,
    },
    {
        "title": "AMP Employment Assistance Cell",
        "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80",
        "display_order": 2,
    },
    {
        "title": "National Talent Search (NTS)",
        "image_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80",
        "display_order": 3,
    },
    {
        "title": "AMP Higher Education Scholarship",
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80",
        "display_order": 4,
    },
]

HOME_GALLERY = [
    {
        "image_url": "https://images.unsplash.com/photo-1692269725836-fbd72e98883f?auto=format&fit=crop&w=900&q=80",
        "alt_text": "Indian schoolchildren seated together in a classroom learning session",
        "title": "Classroom Learning",
        "description": "Students engaged together in a supported classroom learning session.",
        "display_order": 1,
    },
    {
        "image_url": "https://images.unsplash.com/photo-1692269725911-87697c558be1?auto=format&fit=crop&w=900&q=80",
        "alt_text": "Two young Indian girls studying at a school desk with notebooks",
        "title": "Focused Study Time",
        "description": "Young learners building strong foundations through guided study.",
        "display_order": 2,
    },
    {
        "image_url": "https://images.unsplash.com/photo-1692269725827-699e04a11cdf?auto=format&fit=crop&w=900&q=80",
        "alt_text": "Indian boys reading and studying together during an education support session",
        "title": "Reading Together",
        "description": "Peer learning and reading support during an education session.",
        "display_order": 3,
    },
    {
        "image_url": "https://images.unsplash.com/photo-1522661067900-ab829854a57f?auto=format&fit=crop&w=900&q=80",
        "alt_text": "Indian teacher volunteering at a chalkboard to guide students in class",
        "title": "Volunteer Teaching",
        "description": "Dedicated volunteers guiding students through classroom lessons.",
        "display_order": 4,
    },
    {
        "image_url": "https://images.unsplash.com/photo-1759738098462-90ffac98c554?auto=format&fit=crop&w=900&q=80",
        "alt_text": "Rural Indian women engaged in a livelihood weaving and skill development program",
        "title": "Livelihood Skills",
        "description": "Women building sustainable livelihoods through skill development.",
        "display_order": 5,
    },
    {
        "image_url": "https://images.unsplash.com/photo-1542810634-71277d95dcbb?auto=format&fit=crop&w=900&q=80",
        "alt_text": "Indian children learning outdoors during a community education outreach program",
        "title": "Community Outreach",
        "description": "Outdoor learning moments from our community education programs.",
        "display_order": 6,
    },
]

HOME_EVENTS = [
    {
        "title": "Employability Training Programme (ETP)",
        "description": (
            "A comprehensive pre-employment preparation workshop focused on grooming "
            "young graduates. Enhance your skills in resume building, communication, "
            "and mock corporate interview execution."
        ),
        "speaker": "Mr. Tirmizi Ashrafi",
        "event_date": "24 Jul 2026",
        "venue": "Seminar Hall 2, Mumbai Campus",
        "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=300&h=300&q=80",
        "registration_link": "#etp-details",
        "button_text": "View Details",
        "display_order": 1,
    },
    {
        "title": "National Mega Job Fair & Campus Placement Drive",
        "description": (
            "Bridging the gap between skilled, underprivileged youth and top-tier "
            "corporate employers. Open registration platform for multiple industrial "
            "and corporate sectors across India."
        ),
        "speaker": "Corporate HR Panel",
        "event_date": "12 Aug 2026",
        "venue": "Main Exhibition Grounds, Nagpada",
        "image_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=300&h=300&q=80",
        "registration_link": "#job-fair",
        "button_text": "View Details",
        "display_order": 2,
    },
    {
        "title": "Skill Training & Vocational Orientation",
        "description": (
            "Specialized professional career guidance seminar meant to introduce "
            "self-employment micro-financing structures, small-scale business "
            "incubation, and vocational paths."
        ),
        "speaker": "AIF Mentorship Board",
        "event_date": "05 Sep 2026",
        "venue": "Centre of Excellence, Auditorium B",
        "image_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=300&h=300&q=80",
        "registration_link": "#skill-training",
        "button_text": "View Details",
        "display_order": 3,
    },
]

TESTIMONIALS = [
    {
        "name": "Aamir Malik",
        "designation": "ACE Alumnus / UPSC Aspirant",
        "location": "New Delhi",
        "profile_image": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "AMP India Foundations Academy for Competitive Exams provided me with not "
            "just premium resources, but unmatched mentorship from industry experts. "
            "It broke down financial barriers for my civil services preparation."
        ),
        "rating": 5,
        "display_order": 1,
    },
    {
        "name": "Sana Khan",
        "designation": "Placed Candidate",
        "location": "Mumbai Cell",
        "profile_image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "Through AMPs Employment Assistance Cell, I attended a mega job fair and "
            "secured a position as a Software Engineer. Their mock interviews and "
            "soft-skill bootcamps completely changed my career trajectory."
        ),
        "rating": 5,
        "display_order": 2,
    },
    {
        "name": "Imran Shaikh",
        "designation": "Active Chapter Volunteer",
        "location": "Pune Chapter",
        "profile_image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "Volunteering with the National Talent Search (NTS) projects has given me "
            "immense purpose. Seeing grassroots students get access to higher education "
            "scholarships is the ultimate reward."
        ),
        "rating": 5,
        "display_order": 3,
    },
    {
        "name": "Aisha Khan",
        "designation": "Scholarship Recipient",
        "location": "Hyderabad",
        "profile_image": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "AIF's higher education scholarship changed my life. As a meritorious student "
            "from an underprivileged family, I could never afford college fees. AMP India "
            "Foundation funded my degree and connected me with mentors who guided me "
            "through every academic challenge. Today, I am the first graduate in my family."
        ),
        "rating": 5,
        "display_order": 4,
    },
    {
        "name": "Rahul Sharma",
        "designation": "Software Engineer",
        "location": "Bengaluru",
        "profile_image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "After attending AMP's Employability Training Programme, I gained real "
            "confidence in interviews and resume building. The national job fair "
            "organized by AIF connected me directly with recruiters. Within weeks, I "
            "secured a role as a Software Engineer. Their structured approach turned "
            "my potential into a lasting profession."
        ),
        "rating": 5,
        "display_order": 5,
    },
    {
        "name": "Fatima Shaikh",
        "designation": "Volunteer",
        "location": "Mumbai",
        "profile_image": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "Volunteering with AMP India Foundation has been deeply fulfilling. I helped "
            "coordinate medical relief camps and education workshops across Maharashtra. "
            "The professionalism and transparency of the team inspired me to contribute "
            "more. Serving underserved communities through AIF gave my skills a meaningful "
            "purpose beyond the corporate world."
        ),
        "rating": 5,
        "display_order": 6,
    },
    {
        "name": "Imran Siddiqui",
        "designation": "Entrepreneur",
        "location": "Ahmedabad",
        "profile_image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "AIF's vocational training and economic empowerment program helped me launch "
            "my small tailoring business. They provided skill development workshops, "
            "micro-financing guidance, and mentorship on setting up self-help groups. "
            "What started as a single sewing machine is now a livelihood supporting my "
            "entire family."
        ),
        "rating": 5,
        "display_order": 7,
    },
    {
        "name": "Neha Patel",
        "designation": "Parent",
        "location": "Pune",
        "profile_image": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "As a parent, I was worried about my daughter's future until we discovered "
            "AMP's Centres of Excellence. The career counselling and scholarship support "
            "she received transformed her academic journey. AIF bridges the opportunity "
            "gap for deserving children — I am forever grateful for their unbiased approach."
        ),
        "rating": 5,
        "display_order": 8,
    },
    {
        "name": "Mohammed Arif",
        "designation": "Career Guidance Participant",
        "location": "Lucknow",
        "profile_image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=300&h=300&q=80",
        "message": (
            "The career guidance sessions conducted by AIF professionals opened doors I "
            "never knew existed. From choosing the right vocational path to preparing for "
            "employment drives, every step was supported. Their pan-India network of "
            "volunteers truly empowers youth who lack access to quality mentorship and "
            "corporate exposure."
        ),
        "rating": 5,
        "display_order": 9,
    },
]

FEATURED_EVENTS = [
    {
        "title": "Career Guidance & Employment Drive 2026",
        "event_date": "Saturday, 15 March 2026",
        "event_time": "9:00 AM – 5:00 PM",
        "venue": "Mumbai",
        "category": "Employment",
        "description": (
            "A flagship employment initiative connecting skilled youth with leading "
            "corporate employers. Featuring resume clinics, mock interviews, on-spot "
            "hiring, and career counselling by industry professionals."
        ),
        "banner_image": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=900&q=80",
        "display_order": 1,
    },
]

UPCOMING_EVENTS = [
    {
        "title": "Scholarship Awareness & Education Workshop",
        "category": "Education",
        "event_date": "18 Jan 2026",
        "venue": "Delhi NCR",
        "description": (
            "Guiding meritorious underprivileged students on scholarship applications, "
            "higher education pathways, and Centres of Excellence programs."
        ),
        "image_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80",
        "display_order": 1,
    },
    {
        "title": "National Mega Job Fair & Placement Drive",
        "category": "Employment",
        "event_date": "12 Aug 2026",
        "venue": "Mumbai",
        "description": (
            "Bridging skilled youth with top-tier corporate employers across multiple "
            "industrial sectors with on-spot interviews and hiring."
        ),
        "image_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=600&q=80",
        "display_order": 2,
    },
    {
        "title": "Free Medical Camp & Health Screening",
        "category": "Medical Camp",
        "event_date": "22 Aug 2026",
        "venue": "Hyderabad",
        "description": (
            "Providing free health check-ups, critical illness screenings, and medical "
            "relief support for underserved communities."
        ),
        "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80",
        "display_order": 3,
    },
    {
        "title": "Vocational Skill Development Bootcamp",
        "category": "Skill Development",
        "event_date": "05 Sep 2026",
        "venue": "Bengaluru",
        "description": (
            "Intensive vocational training in digital skills, tailoring, and small-scale "
            "entrepreneurship for sustainable livelihoods."
        ),
        "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80",
        "display_order": 4,
    },
    {
        "title": "Student Mentorship & Career Guidance Summit",
        "category": "Career Guidance",
        "event_date": "14 Oct 2026",
        "venue": "Pune",
        "description": (
            "One-on-one mentoring sessions with industry professionals to guide students "
            "through academic and career decision-making."
        ),
        "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80",
        "display_order": 5,
    },
    {
        "title": "Community Outreach & Upliftment Drive",
        "category": "Community Outreach",
        "event_date": "12 Dec 2026",
        "venue": "Kolkata",
        "description": (
            "Grassroots community development initiative distributing essential supplies, "
            "financial literacy workshops, and self-help group setups."
        ),
        "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=600&q=80",
        "display_order": 6,
    },
]

GALLERY_ITEMS = [
    {
        "title": "National Job Fair 2025",
        "event_date": "15 Mar 2025",
        "event_time": "9:00 AM – 5:00 PM",
        "venue": "Mumbai",
        "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=600&q=80",
        "category": "Employment",
        "description": (
            "A large-scale placement drive connecting skilled youth with corporate "
            "employers across manufacturing, IT, and services."
        ),
        "display_order": 1,
    },
    {
        "title": "Medical Relief Camp",
        "event_date": "22 Jun 2025",
        "event_time": "8:00 AM – 2:00 PM",
        "venue": "Hyderabad",
        "image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80",
        "category": "Medical Camp",
        "description": (
            "Free health check-ups, screenings, and medical relief support delivered "
            "to underserved neighbourhoods."
        ),
        "display_order": 2,
    },
    {
        "title": "Scholarship Distribution Ceremony",
        "event_date": "10 Dec 2024",
        "event_time": "11:00 AM – 1:00 PM",
        "venue": "Delhi",
        "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=600&q=80",
        "category": "Education",
        "description": (
            "Recognising meritorious students and awarding scholarships to support "
            "higher education pathways."
        ),
        "display_order": 3,
    },
    {
        "title": "Skill Training Graduation",
        "event_date": "18 Sep 2024",
        "event_time": "10:00 AM – 12:30 PM",
        "venue": "Bengaluru",
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80",
        "category": "Skill Development",
        "description": (
            "Celebrating graduates of vocational programs in digital skills, "
            "tailoring, and entrepreneurship."
        ),
        "display_order": 4,
    },
    {
        "title": "Mentorship Summit",
        "event_date": "05 Aug 2024",
        "event_time": "10:00 AM – 4:00 PM",
        "venue": "Pune",
        "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80",
        "category": "Career Guidance",
        "description": (
            "Industry mentors guided students through academic choices, resume "
            "building, and career planning."
        ),
        "display_order": 5,
    },
    {
        "title": "Community Upliftment Drive",
        "event_date": "12 Nov 2023",
        "event_time": "9:30 AM – 1:30 PM",
        "venue": "Kolkata",
        "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=600&q=80",
        "category": "Community Outreach",
        "description": (
            "Grassroots outreach with essential supplies, financial literacy "
            "workshops, and self-help group support."
        ),
        "display_order": 6,
    },
]


def upsert(model, match_filters: dict, payload: dict) -> str:
    """Insert or update a row. Returns 'created' or 'updated'."""
    payload = {**payload, "status": "published"}
    row = model.query.filter_by(**match_filters).first()
    if row:
        for key, value in payload.items():
            setattr(row, key, value)
        return "updated"
    db.session.add(model(**payload))
    return "created"


def seed_collection(label, model, items, match_key: str, name_key: str = "title"):
    created = updated = 0
    for item in items:
        action = upsert(model, {match_key: item[match_key]}, item)
        if action == "created":
            created += 1
        else:
            updated += 1
    print(f"  {label}: {created} created, {updated} updated ({len(items)} total)")


NAVBAR_ITEMS = [
    {"label": "HOME", "href": "/home", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 1},
    {"label": "ABOUT US", "href": "/about", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 2},
    {"label": "PROJECTS", "href": "/projects/education", "item_type": "dropdown", "item_key": "projects", "parent_key": None, "display_order": 3},
    {"label": "Education", "href": "/projects/education", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 4},
    {"label": "Medical Relief", "href": "/projects/medical", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 5},
    {"label": "Employment Support", "href": "/projects/employment", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 6},
    {"label": "Economic Empowerment", "href": "/projects/empowerment", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 7},
    {"label": "Student Mentorship", "href": "/projects/mentorship", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 8},
    {"label": "Employment Training", "href": "/projects/training", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 9},
    {"label": "EVENTS", "href": "/events", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 10},
    {"label": "VOLUNTEER", "href": "/volunteer", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 11},
    {"label": "SUPPORT US", "href": "/support-us", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 12},
    {"label": "CONTACT", "href": "/contact", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 13},
]

FOOTER_LINKS = [
    {"label": "Home", "href": "/", "display_order": 1},
    {"label": "About Us", "href": "/about", "display_order": 2},
    {"label": "What We Do", "href": "/what-we-do", "display_order": 3},
    {"label": "Projects", "href": "/projects", "display_order": 4},
    {"label": "Events", "href": "/events", "display_order": 5},
    {"label": "Join Us / Volunteer", "href": "/volunteer", "display_order": 6},
    {"label": "Support Us", "href": "/support-us", "display_order": 7},
    {"label": "Contact", "href": "/contact", "display_order": 8},
    {"label": "Terms & Conditions", "href": "/terms-and-conditions", "display_order": 9},
]

FOOTER_FOCUS = [
    {"title": "National Talent Search Examination", "href": "/projects/education", "date_label": "July 2026", "display_order": 1},
    {"title": "Employability Training Programs", "href": "/projects/training", "date_label": "June 2026", "display_order": 2},
    {"title": "Higher Education Scholarship Distribution", "href": "/projects/education", "date_label": "May 2026", "display_order": 3},
]

FOOTER_SETTINGS = {
    "cta_heading": "Join Our Mission to Empower Lives Through Education & Employment.",
    "cta_button_text": "BECOME A VOLUNTEER",
    "cta_button_link": "/volunteer",
    "about_heading": "ABOUT US",
    "about_text": (
        "AMP India Foundation is a non-profit organization dedicated to regularise "
        "and scale up socio-economic development welfare activities. We empower "
        "underprivileged youth through sustainable educational models, rigorous training, "
        "and professional mentorship."
    ),
    "about_link_text": "READ MORE →",
    "about_link_href": "/about",
    "useful_links_heading": "USEFUL LINKS",
    "recent_focus_heading": "RECENT FOCUS",
    "contact_heading": "GET IN TOUCH",
    "address_label": "📍 Address:",
    "address_text": "AMP India Foundation, Mumbai, Maharashtra, India.",
    "phone_label": "📞 Phone:",
    "phone_text": "+91 93200 60093",
    "email_label": "✉️ Email:",
    "email_text": "info@ampindia.org",
    "follow_heading": "FOLLOW US",
    "facebook_url": "https://www.facebook.com/ampindiafoundation/",
    "instagram_url": "https://www.instagram.com/ampindiafoundation/",
    "copyright_text": "Copyrights © 2026 All Rights Reserved. Powered by ",
    "copyright_highlight": "AMP India Foundation",
}


def seed_navbar_settings():
    row = NavbarSettings.query.order_by(NavbarSettings.id.asc()).first()
    payload = {
        "logo_url": "/assets/logo.png",
        "logo_alt": "AMP Logo",
        "logo_link": "/",
    }
    if row:
        for key, value in payload.items():
            setattr(row, key, value)
        print("  Navbar settings: updated")
    else:
        db.session.add(NavbarSettings(**payload, created_at=utcnow(), updated_at=utcnow()))
        print("  Navbar settings: created")


def seed_footer_settings():
    row = FooterSettings.query.order_by(FooterSettings.id.asc()).first()
    if row:
        for key, value in FOOTER_SETTINGS.items():
            setattr(row, key, value)
        print("  Footer settings: updated")
    else:
        db.session.add(FooterSettings(**FOOTER_SETTINGS, created_at=utcnow(), updated_at=utcnow()))
        print("  Footer settings: created")


def seed_navbar_items():
    created = updated = 0
    for item in NAVBAR_ITEMS:
        filters = {"label": item["label"], "href": item["href"]}
        if item.get("parent_key"):
            filters["parent_key"] = item["parent_key"]
        else:
            filters["parent_key"] = None
        action = upsert(NavbarItem, filters, item)
        if action == "created":
            created += 1
        else:
            updated += 1
    print(f"  Navbar items: {created} created, {updated} updated ({len(NAVBAR_ITEMS)} total)")


def main():
    app = create_app()
    with app.app_context():
        print("Seeding website content into MySQL…")
        seed_collection("Hero banners", HeroBanner, HERO_BANNERS, "title")
        seed_collection("Home projects", HomeProject, HOME_PROJECTS, "title")
        seed_collection("Home gallery", HomeGalleryItem, HOME_GALLERY, "alt_text")
        seed_collection("Home events", HomeEvent, HOME_EVENTS, "title")
        seed_collection("Testimonials", Testimonial, TESTIMONIALS, "name", "name")
        seed_collection("Featured events", FeaturedEvent, FEATURED_EVENTS, "title")
        seed_collection("Upcoming events", UpcomingEvent, UPCOMING_EVENTS, "title")
        seed_collection("Past events", GalleryItem, GALLERY_ITEMS, "title")
        seed_navbar_settings()
        seed_navbar_items()
        seed_footer_settings()
        seed_collection("Footer links", FooterLink, FOOTER_LINKS, "label")
        seed_collection("Footer focus", FooterFocusItem, FOOTER_FOCUS, "title")
        db.session.commit()
        print("Done. All seeded items are status=published.")


if __name__ == "__main__":
    main()
