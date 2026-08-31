import re
from typing import Dict, List, Optional

class PlatformGenerator:
    """Generate platform-specific variants from blog post content"""
    
    # Platform constraints
    CONSTRAINTS = {
        "twitter": {
            "max_length": 280,
            "max_hashtags": 3,
            "tone": "concise",
            "description": "Short, attention-grabbing posts with hashtags"
        },
        "linkedin": {
            "max_length": 3000,
            "max_hashtags": 5,
            "tone": "professional",
            "description": "Professional, detailed posts with industry insights"
        },
        "discord": {
            "max_length": 2000,
            "max_hashtags": 0,
            "tone": "casual",
            "description": "Casual, community-friendly updates"
        },
        "mock_x": {
            "max_length": 280,
            "max_hashtags": 3,
            "tone": "concise",
            "description": "Mock Twitter/X style"
        },
        "mock_linkedin": {
            "max_length": 3000,
            "max_hashtags": 5,
            "tone": "professional",
            "description": "Mock LinkedIn style"
        }
    }
    
    @staticmethod
    def extract_key_points(content: str, max_points: int = 3) -> List[str]:
        """Extract key points from content"""
        # Look for bullet points or numbered lists
        points = []
        
        # Find markdown bullet points
        bullet_pattern = r'[-*]\s+(.*?)(?:\n|$)'
        bullet_matches = re.findall(bullet_pattern, content)
        if bullet_matches:
            points.extend([p.strip() for p in bullet_matches[:max_points]])
        
        # Find numbered lists
        number_pattern = r'\d+\.\s+(.*?)(?:\n|$)'
        number_matches = re.findall(number_pattern, content)
        if number_matches:
            points.extend([p.strip() for p in number_matches[:max_points - len(points)]])
        
        # If no bullet points, use sentences
        if not points:
            sentences = re.split(r'[.!?]+\s+', content)
            points = [s.strip() for s in sentences if len(s.strip()) > 20][:max_points]
        
        # Clean up points
        points = [p.replace('\n', ' ').strip() for p in points if p]
        
        # If still no points, use first paragraph
        if not points:
            paragraphs = content.split('\n\n')
            if paragraphs:
                first_para = paragraphs[0].replace('\n', ' ').strip()
                if first_para:
                    points = [first_para[:150]]
        
        return points[:max_points]
    
    @staticmethod
    def generate_twitter_variant(title: str, content: str) -> Dict:
        """Generate Twitter/X variant (280 chars max)"""
        key_points = PlatformGenerator.extract_key_points(content, 2)
        
        # Build tweet
        if key_points:
            tweet = f"{title}: {key_points[0]}"
        else:
            # Use first sentence
            sentences = content.split('.')
            if sentences:
                first_sentence = sentences[0].strip()
                tweet = f"{title}: {first_sentence[:200]}"
            else:
                tweet = f"{title}: {content[:200]}"
        
        # Truncate to 280 characters
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        # Add hashtags
        hashtags = [f"#{''.join(word.capitalize() for word in title.split()[:2])}"] if title else []
        hashtags.extend(["#Tech", "#Innovation"] if "tech" in content.lower() else ["#Update"])
        hashtags = hashtags[:3]
        
        return {
            "content": tweet,
            "hashtags": " ".join(hashtags),
            "platform": "twitter"
        }
    
    @staticmethod
    def generate_linkedin_variant(title: str, content: str) -> Dict:
        """Generate LinkedIn variant (professional, detailed)"""
        key_points = PlatformGenerator.extract_key_points(content, 3)
        
        # Build professional post
        lines = [
            f"📊 {title}",
            "",
            f"{content[:300]}..."
            ""
        ]
        
        if key_points:
            lines.append("Key Takeaways:")
            for i, point in enumerate(key_points, 1):
                lines.append(f"{i}. {point}")
        
        lines.extend([
            "",
            "What are your thoughts on this? Let's discuss in the comments! 👇",
            "",
            "#ProfessionalInsights #IndustryUpdate"
        ])
        
        linkedin_content = "\n".join(lines)
        
        # Truncate if needed
        if len(linkedin_content) > 3000:
            linkedin_content = linkedin_content[:2997] + "..."
        
        return {
            "content": linkedin_content,
            "hashtags": "#ProfessionalInsights #IndustryUpdate",
            "platform": "linkedin"
        }
    
    @staticmethod
    def generate_discord_variant(title: str, content: str) -> Dict:
        """Generate Discord variant (casual, community-friendly)"""
        key_points = PlatformGenerator.extract_key_points(content, 2)
        
        # Build casual post
        lines = [
            f"**📢 {title}**",
            "",
            f"Hey everyone! Check this out:",
            "",
            f"{content[:200]}..."
            ""
        ]
        
        if key_points:
            lines.append("**Quick highlights:**")
            for point in key_points:
                lines.append(f"• {point}")
        
        lines.extend([
            "",
            "What do you all think? Drop your thoughts below! 💬"
        ])
        
        discord_content = "\n".join(lines)
        
        # Truncate if needed
        if len(discord_content) > 2000:
            discord_content = discord_content[:1997] + "..."
        
        return {
            "content": discord_content,
            "hashtags": "",
            "platform": "discord"
        }
    
    @staticmethod
    def generate_mock_x_variant(title: str, content: str) -> Dict:
        """Generate Mock X (Twitter-like) variant"""
        return PlatformGenerator.generate_twitter_variant(title, content)
    
    @staticmethod
    def generate_mock_linkedin_variant(title: str, content: str) -> Dict:
        """Generate Mock LinkedIn variant"""
        return PlatformGenerator.generate_linkedin_variant(title, content)
    
    @staticmethod
    def generate_variant(platform: str, title: str, content: str) -> Optional[Dict]:
        """Generate a variant for a specific platform"""
        generators = {
            "twitter": PlatformGenerator.generate_twitter_variant,
            "linkedin": PlatformGenerator.generate_linkedin_variant,
            "discord": PlatformGenerator.generate_discord_variant,
            "mock_x": PlatformGenerator.generate_mock_x_variant,
            "mock_linkedin": PlatformGenerator.generate_mock_linkedin_variant
        }
        
        generator = generators.get(platform.lower())
        if generator:
            return generator(title, content)
        return None
