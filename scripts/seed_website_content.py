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
    GalleryItem,
    HeroBanner,
    HomeEvent,
    HomeProject,
    Testimonial,
    UpcomingEvent,
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
        "description": "Premium coaching and mentorship for competitive exam aspirants.",
        "image_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=600&q=80",
        "button_text": "View Project",
        "button_link": "/projects",
        "display_order": 1,
    },
    {
        "title": "AMP Employment Assistance Cell",
        "description": "Connecting skilled youth with employers through training and job fairs.",
        "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80",
        "button_text": "View Project",
        "button_link": "/projects",
        "display_order": 2,
    },
    {
        "title": "National Talent Search (NTS)",
        "description": "Identifying and nurturing talented students across India.",
        "image_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80",
        "button_text": "View Project",
        "button_link": "/projects",
        "display_order": 3,
    },
    {
        "title": "AMP Higher Education Scholarship",
        "description": "Scholarships enabling meritorious students to pursue higher education.",
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80",
        "button_text": "View Project",
        "button_link": "/projects",
        "display_order": 4,
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
        "year": "2025",
        "location": "Mumbai",
        "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=600&q=80",
        "category": "Employment",
        "alt_text": "National Job Fair 2025",
        "display_order": 1,
    },
    {
        "title": "Medical Relief Camp",
        "year": "2025",
        "location": "Hyderabad",
        "image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80",
        "category": "Medical Camp",
        "alt_text": "Medical Relief Camp",
        "display_order": 2,
    },
    {
        "title": "Scholarship Distribution",
        "year": "2024",
        "location": "Delhi",
        "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=600&q=80",
        "category": "Education",
        "alt_text": "Scholarship Distribution",
        "display_order": 3,
    },
    {
        "title": "Skill Training Graduation",
        "year": "2024",
        "location": "Bengaluru",
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80",
        "category": "Skill Development",
        "alt_text": "Skill Training Graduation",
        "display_order": 4,
    },
    {
        "title": "Mentorship Summit",
        "year": "2024",
        "location": "Pune",
        "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80",
        "category": "Career Guidance",
        "alt_text": "Mentorship Summit",
        "display_order": 5,
    },
    {
        "title": "Community Upliftment Drive",
        "year": "2023",
        "location": "Kolkata",
        "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=600&q=80",
        "category": "Community Outreach",
        "alt_text": "Community Upliftment Drive",
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


def main():
    app = create_app()
    with app.app_context():
        print("Seeding website content into MySQL…")
        seed_collection("Hero banners", HeroBanner, HERO_BANNERS, "title")
        seed_collection("Home projects", HomeProject, HOME_PROJECTS, "title")
        seed_collection("Home events", HomeEvent, HOME_EVENTS, "title")
        seed_collection("Testimonials", Testimonial, TESTIMONIALS, "name", "name")
        seed_collection("Featured events", FeaturedEvent, FEATURED_EVENTS, "title")
        seed_collection("Upcoming events", UpcomingEvent, UPCOMING_EVENTS, "title")
        seed_collection("Gallery items", GalleryItem, GALLERY_ITEMS, "title")
        db.session.commit()
        print("Done. All seeded items are status=published.")


if __name__ == "__main__":
    main()
