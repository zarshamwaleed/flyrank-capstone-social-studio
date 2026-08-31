from typing import Dict, List, Tuple, Optional
from app.generators import PlatformGenerator

class ConstraintValidator:
    """Validate variants against platform constraints"""
    
    @staticmethod
    def get_platform_constraints(platform: str) -> Optional[Dict]:
        """Get constraints for a specific platform"""
        return PlatformGenerator.CONSTRAINTS.get(platform.lower())
    
    @staticmethod
    def validate_content_length(content: str, max_length: int) -> Tuple[bool, str]:
        """Validate content length"""
        content_length = len(content)
        if content_length > max_length:
            return False, f"Content exceeds maximum length of {max_length} characters (current: {content_length})"
        return True, f"Content length is valid ({content_length}/{max_length})"
    
    @staticmethod
    def validate_hashtags(content: str, max_hashtags: int) -> Tuple[bool, str]:
        """Validate hashtag count"""
        import re
        hashtags = re.findall(r'#\w+', content)
        hashtag_count = len(hashtags)
        
        if hashtag_count > max_hashtags:
            return False, f"Too many hashtags: {hashtag_count} (max: {max_hashtags})"
        return True, f"Hashtag count is valid ({hashtag_count}/{max_hashtags})"
    
    @staticmethod
    def validate_tone(content: str, expected_tone: str) -> Tuple[bool, str]:
        """Validate tone (basic check)"""
        # Simple tone detection based on keywords
        tone_keywords = {
            "professional": ["analyze", "strategy", "insight", "market", "industry", "research", "develop", "implement"],
            "concise": ["quick", "fast", "short", "brief", "summary", "key", "essential"],
            "casual": ["hey", "guys", "awesome", "cool", "check", "nice", "great", "amazing"]
        }
        
        tone_match = {
            "professional": 0,
            "concise": 0,
            "casual": 0
        }
        
        lower_content = content.lower()
        for tone, keywords in tone_keywords.items():
            for keyword in keywords:
                if keyword in lower_content:
                    tone_match[tone] += 1
        
        # Check if expected tone is present
        if tone_match.get(expected_tone, 0) > 0:
            return True, f"Tone appears to be {expected_tone}"
        else:
            # If no match, still pass but warn
            return True, f"Could not detect {expected_tone} tone, but proceeding"
    
    @staticmethod
    def validate_variant(platform: str, content: str, hashtags: Optional[str] = None) -> Dict:
        """Validate a variant against platform constraints"""
        constraints = ConstraintValidator.get_platform_constraints(platform)
        if not constraints:
            return {
                "valid": False,
                "errors": [f"Unknown platform: {platform}"],
                "warnings": [],
                "details": {}
            }
        
        errors = []
        warnings = []
        details = {}
        
        # Validate content length
        is_valid, message = ConstraintValidator.validate_content_length(
            content, constraints["max_length"]
        )
        details["length"] = {"valid": is_valid, "message": message}
        if not is_valid:
            errors.append(message)
        
        # Validate hashtags
        full_content = content
        if hashtags:
            full_content = f"{content} {hashtags}"
        
        is_valid, message = ConstraintValidator.validate_hashtags(
            full_content, constraints["max_hashtags"]
        )
        details["hashtags"] = {"valid": is_valid, "message": message}
        if not is_valid:
            errors.append(message)
        
        # Validate tone (warning only, not blocking)
        is_valid, message = ConstraintValidator.validate_tone(
            content, constraints["tone"]
        )
        details["tone"] = {"valid": is_valid, "message": message}
        if not is_valid:
            warnings.append(message)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": details,
            "constraints": constraints
        }
    
    @staticmethod
    def validate_all_variants(variants: List[Dict]) -> Dict:
        """Validate multiple variants"""
        results = {}
        all_valid = True
        
        for variant in variants:
            platform = variant.get("platform", "").lower()
            content = variant.get("content", "")
            hashtags = variant.get("hashtags", "")
            
            result = ConstraintValidator.validate_variant(platform, content, hashtags)
            results[platform] = result
            
            if not result["valid"]:
                all_valid = False
        
        return {
            "all_valid": all_valid,
            "results": results
        }
    
    @staticmethod
    def get_constraints_summary() -> Dict:
        """Get summary of all platform constraints"""
        constraints = PlatformGenerator.CONSTRAINTS
        summary = {}
        
        for platform, rules in constraints.items():
            summary[platform] = {
                "max_length": rules["max_length"],
                "max_hashtags": rules["max_hashtags"],
                "tone": rules["tone"],
                "description": rules["description"]
            }
        
        return summary
