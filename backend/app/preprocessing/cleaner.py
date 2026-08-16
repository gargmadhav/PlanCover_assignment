import re

class TextCleaner:
    @staticmethod
    def reverse_string_if_needed(text: str) -> str:
        """
        Detects if a string or line appears reversed (e.g. '.noitaticilos fo rettam tcejbus eht si ecnarusnI')
        and reverses it if needed.
        """
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # If line contains reversed known disclaimer snippet like 'noitaticilos' or 'ecnarusnI'
            if 'noitaticilos' in stripped or 'ecnarusnI' in stripped or 'ytrebiL' in stripped:
                cleaned_lines.append(stripped[::-1])
            else:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    @staticmethod
    def clean_page_text(text: str) -> str:
        """
        Cleans text by removing null bytes, fixing reversed text snippets,
        normalizing excessive blank spaces and broken glyph artifacts.
        """
        if not text:
            return ""
            
        # Fix reversed lines
        text = TextCleaner.reverse_string_if_needed(text)
        
        # Remove null bytes and unusual control characters
        text = text.replace('\x00', '')
        
        # Normalize multiple vertical spaces
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Normalize double horizontal spaces
        lines = [re.sub(r'[ \t]{2,}', ' ', line).strip() for line in text.split('\n')]
        
        return '\n'.join(lines).strip()
