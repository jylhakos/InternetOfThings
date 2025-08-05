#!/usr/bin/env python3
"""
Data Wrangling and Exploration Tools for BERT Fine-tuning
Provides comprehensive data analysis, cleaning, and exploration capabilities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter
from textstat import flesch_reading_ease, flesch_kincaid_grade
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DataExplorer:
    """Comprehensive data exploration and analysis for text datasets"""
    
    def __init__(self, df: pd.DataFrame, text_column: str, label_column: str):
        self.df = df.copy()
        self.text_column = text_column
        self.label_column = label_column
        self.stats = {}
    
    def basic_statistics(self) -> Dict:
        """Generate basic dataset statistics"""
        print("="*70)
        print("📊 BASIC DATASET STATISTICS")
        print("="*70)
        
        stats = {
            'total_samples': len(self.df),
            'unique_samples': self.df[self.text_column].nunique(),
            'duplicate_samples': len(self.df) - self.df[self.text_column].nunique(),
            'missing_text': self.df[self.text_column].isnull().sum(),
            'missing_labels': self.df[self.label_column].isnull().sum(),
            'empty_text': (self.df[self.text_column].str.strip() == '').sum(),
        }
        
        # Label distribution
        label_counts = self.df[self.label_column].value_counts()
        stats['label_distribution'] = label_counts.to_dict()
        stats['num_classes'] = len(label_counts)
        
        # Text length statistics
        self.df['text_length'] = self.df[self.text_column].str.len()
        self.df['word_count'] = self.df[self.text_column].str.split().str.len()
        
        stats['text_length'] = {
            'mean': self.df['text_length'].mean(),
            'median': self.df['text_length'].median(),
            'min': self.df['text_length'].min(),
            'max': self.df['text_length'].max(),
            'std': self.df['text_length'].std()
        }
        
        stats['word_count'] = {
            'mean': self.df['word_count'].mean(),
            'median': self.df['word_count'].median(),
            'min': self.df['word_count'].min(),
            'max': self.df['word_count'].max(),
            'std': self.df['word_count'].std()
        }
        
        self.stats = stats
        self._print_basic_stats(stats)
        return stats
    
    def _print_basic_stats(self, stats: Dict):
        """Print basic statistics in formatted way"""
        print(f"📈 Total Samples: {stats['total_samples']:,}")
        print(f"🔄 Unique Samples: {stats['unique_samples']:,}")
        print(f"📋 Duplicate Samples: {stats['duplicate_samples']:,}")
        print(f"❌ Missing Text: {stats['missing_text']:,}")
        print(f"❌ Missing Labels: {stats['missing_labels']:,}")
        print(f"📄 Empty Text: {stats['empty_text']:,}")
        print(f"🏷️  Number of Classes: {stats['num_classes']}")
        
        print("\n📊 Label Distribution:")
        for label, count in stats['label_distribution'].items():
            percentage = (count / stats['total_samples']) * 100
            print(f"   {label}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n📝 Text Length Statistics:")
        print(f"   Mean: {stats['text_length']['mean']:.1f} characters")
        print(f"   Median: {stats['text_length']['median']:.1f} characters") 
        print(f"   Range: {stats['text_length']['min']:.0f} - {stats['text_length']['max']:.0f} characters")
        
        print(f"\n📝 Word Count Statistics:")
        print(f"   Mean: {stats['word_count']['mean']:.1f} words")
        print(f"   Median: {stats['word_count']['median']:.1f} words")
        print(f"   Range: {stats['word_count']['min']:.0f} - {stats['word_count']['max']:.0f} words")
    
    def text_quality_analysis(self) -> Dict:
        """Analyze text quality metrics"""
        print("\n" + "="*70)
        print("🔍 TEXT QUALITY ANALYSIS")
        print("="*70)
        
        quality_stats = {}
        
        # Sample texts for analysis (to avoid memory issues with large datasets)
        sample_size = min(1000, len(self.df))
        sample_df = self.df.sample(n=sample_size, random_state=42)
        
        print(f"Analyzing {sample_size} sample texts...")
        
        # Reading complexity
        reading_scores = []
        grade_levels = []
        
        for text in sample_df[self.text_column]:
            if pd.notna(text) and len(str(text).strip()) > 0:
                try:
                    score = flesch_reading_ease(str(text))
                    grade = flesch_kincaid_grade(str(text))
                    reading_scores.append(score)
                    grade_levels.append(grade)
                except:
                    continue
        
        if reading_scores:
            quality_stats['readability'] = {
                'flesch_ease_mean': np.mean(reading_scores),
                'flesch_ease_std': np.std(reading_scores),
                'grade_level_mean': np.mean(grade_levels),
                'grade_level_std': np.std(grade_levels)
            }
        
        # Character distribution
        all_text = ' '.join(sample_df[self.text_column].astype(str))
        
        # Count different character types
        quality_stats['character_analysis'] = {
            'total_chars': len(all_text),
            'alphabetic_ratio': sum(c.isalpha() for c in all_text) / len(all_text),
            'numeric_ratio': sum(c.isdigit() for c in all_text) / len(all_text),
            'space_ratio': sum(c.isspace() for c in all_text) / len(all_text),
            'punctuation_ratio': sum(not c.isalnum() and not c.isspace() for c in all_text) / len(all_text)
        }
        
        # Language patterns
        urls = sample_df[self.text_column].str.contains(r'http[s]?://|www\.', na=False).sum()
        emails = sample_df[self.text_column].str.contains(r'\S+@\S+', na=False).sum()
        phone_numbers = sample_df[self.text_column].str.contains(r'\d{3}-?\d{3}-?\d{4}', na=False).sum()
        
        quality_stats['content_patterns'] = {
            'texts_with_urls': urls,
            'texts_with_emails': emails,
            'texts_with_phone_numbers': phone_numbers,
            'url_percentage': (urls / sample_size) * 100,
            'email_percentage': (emails / sample_size) * 100
        }
        
        self._print_quality_stats(quality_stats)
        return quality_stats
    
    def _print_quality_stats(self, stats: Dict):
        """Print quality statistics"""
        if 'readability' in stats:
            print(f"📖 Readability (Flesch Reading Ease): {stats['readability']['flesch_ease_mean']:.1f} ± {stats['readability']['flesch_ease_std']:.1f}")
            print(f"🎓 Grade Level (Flesch-Kincaid): {stats['readability']['grade_level_mean']:.1f} ± {stats['readability']['grade_level_std']:.1f}")
        
        if 'character_analysis' in stats:
            char_stats = stats['character_analysis']
            print(f"\n📝 Character Distribution:")
            print(f"   Alphabetic: {char_stats['alphabetic_ratio']:.1%}")
            print(f"   Numeric: {char_stats['numeric_ratio']:.1%}")
            print(f"   Whitespace: {char_stats['space_ratio']:.1%}")
            print(f"   Punctuation: {char_stats['punctuation_ratio']:.1%}")
        
        if 'content_patterns' in stats:
            patterns = stats['content_patterns']
            print(f"\n🔗 Content Patterns:")
            print(f"   URLs: {patterns['texts_with_urls']} ({patterns['url_percentage']:.1f}%)")
            print(f"   Emails: {patterns['texts_with_emails']} ({patterns['email_percentage']:.1f}%)")
            print(f"   Phone Numbers: {patterns['texts_with_phone_numbers']}")
    
    def vocabulary_analysis(self, top_n: int = 50) -> Dict:
        """Analyze vocabulary and word frequencies"""
        print("\n" + "="*70)
        print("📚 VOCABULARY ANALYSIS")
        print("="*70)
        
        # Combine all text and clean
        all_text = ' '.join(self.df[self.text_column].astype(str).str.lower())
        
        # Basic cleaning
        all_text = re.sub(r'[^\w\s]', ' ', all_text)
        words = all_text.split()
        
        # Word frequency analysis
        word_freq = Counter(words)
        vocab_stats = {
            'total_words': len(words),
            'unique_words': len(word_freq),
            'vocabulary_diversity': len(word_freq) / len(words),
            'top_words': dict(word_freq.most_common(top_n))
        }
        
        # Words by length
        word_lengths = [len(word) for word in words]
        vocab_stats['word_length'] = {
            'mean': np.mean(word_lengths),
            'median': np.median(word_lengths),
            'min': min(word_lengths),
            'max': max(word_lengths),
            'std': np.std(word_lengths)
        }
        
        # Rare words (appearing only once)
        rare_words = [word for word, count in word_freq.items() if count == 1]
        vocab_stats['rare_words_count'] = len(rare_words)
        vocab_stats['rare_words_ratio'] = len(rare_words) / len(word_freq)
        
        self._print_vocab_stats(vocab_stats, top_n)
        return vocab_stats
    
    def _print_vocab_stats(self, stats: Dict, top_n: int):
        """Print vocabulary statistics"""
        print(f"📊 Total Words: {stats['total_words']:,}")
        print(f"🔤 Unique Words: {stats['unique_words']:,}")
        print(f"🎯 Vocabulary Diversity: {stats['vocabulary_diversity']:.4f}")
        print(f"📏 Average Word Length: {stats['word_length']['mean']:.1f} characters")
        print(f"🔍 Rare Words (appear once): {stats['rare_words_count']:,} ({stats['rare_words_ratio']:.1%})")
        
        print(f"\n🔥 Top {top_n} Most Common Words:")
        for i, (word, count) in enumerate(list(stats['top_words'].items())[:20], 1):
            print(f"   {i:2d}. {word}: {count:,}")
    
    def label_distribution_analysis(self) -> Dict:
        """Analyze label distribution and class balance"""
        print("\n" + "="*70)
        print("🏷️  LABEL DISTRIBUTION ANALYSIS")
        print("="*70)
        
        label_stats = {}
        
        # Basic distribution
        counts = self.df[self.label_column].value_counts()
        percentages = self.df[self.label_column].value_counts(normalize=True) * 100
        
        label_stats['distribution'] = counts.to_dict()
        label_stats['percentages'] = percentages.to_dict()
        
        # Class balance analysis
        max_count = counts.max()
        min_count = counts.min()
        label_stats['imbalance_ratio'] = max_count / min_count
        label_stats['is_balanced'] = label_stats['imbalance_ratio'] <= 2.0
        
        # Text length by label
        length_by_label = self.df.groupby(self.label_column)['text_length'].agg(['mean', 'median', 'std'])
        label_stats['text_length_by_label'] = length_by_label.to_dict()
        
        # Word count by label
        word_count_by_label = self.df.groupby(self.label_column)['word_count'].agg(['mean', 'median', 'std'])
        label_stats['word_count_by_label'] = word_count_by_label.to_dict()
        
        self._print_label_stats(label_stats)
        return label_stats
    
    def _print_label_stats(self, stats: Dict):
        """Print label distribution statistics"""
        print(f"⚖️  Class Balance Ratio: {stats['imbalance_ratio']:.2f}")
        print(f"✅ Balanced Dataset: {'Yes' if stats['is_balanced'] else 'No'}")
        
        print(f"\n📊 Label Distribution:")
        for label in stats['distribution']:
            count = stats['distribution'][label]
            pct = stats['percentages'][label]
            print(f"   {label}: {count:,} samples ({pct:.1f}%)")
        
        print(f"\n📝 Average Text Length by Label:")
        for label in stats['text_length_by_label']['mean']:
            mean_len = stats['text_length_by_label']['mean'][label]
            print(f"   {label}: {mean_len:.0f} characters")
    
    def detect_data_issues(self) -> Dict:
        """Detect potential data quality issues"""
        print("\n" + "="*70)
        print("🔍 DATA QUALITY ISSUES DETECTION")
        print("="*70)
        
        issues = {
            'missing_data': {},
            'duplicates': {},
            'outliers': {},
            'inconsistencies': {}
        }
        
        # Missing data
        issues['missing_data'] = {
            'missing_text': self.df[self.text_column].isnull().sum(),
            'missing_labels': self.df[self.label_column].isnull().sum(),
            'empty_text': (self.df[self.text_column].str.strip() == '').sum()
        }
        
        # Duplicates
        text_duplicates = self.df[self.text_column].duplicated().sum()
        exact_duplicates = self.df.duplicated().sum()
        issues['duplicates'] = {
            'duplicate_texts': text_duplicates,
            'exact_duplicates': exact_duplicates
        }
        
        # Outliers in text length
        q1 = self.df['text_length'].quantile(0.25)
        q3 = self.df['text_length'].quantile(0.75)
        iqr = q3 - q1
        outlier_threshold_low = q1 - 1.5 * iqr
        outlier_threshold_high = q3 + 1.5 * iqr
        
        length_outliers = ((self.df['text_length'] < outlier_threshold_low) | 
                          (self.df['text_length'] > outlier_threshold_high)).sum()
        
        issues['outliers'] = {
            'text_length_outliers': length_outliers,
            'very_short_texts': (self.df['text_length'] < 10).sum(),
            'very_long_texts': (self.df['text_length'] > 5000).sum()
        }
        
        # Inconsistencies
        mixed_case_labels = 0
        if self.df[self.label_column].dtype == 'object':
            # Check for labels that might be the same but with different cases
            unique_labels = self.df[self.label_column].unique()
            lower_labels = [str(label).lower() for label in unique_labels if pd.notna(label)]
            mixed_case_labels = len(unique_labels) - len(set(lower_labels))
        
        issues['inconsistencies'] = {
            'mixed_case_labels': mixed_case_labels,
            'texts_with_only_punctuation': (self.df[self.text_column].str.replace(r'[^\w\s]', '', regex=True).str.strip() == '').sum()
        }
        
        self._print_data_issues(issues)
        return issues
    
    def _print_data_issues(self, issues: Dict):
        """Print detected data issues"""
        total_issues = 0
        
        print("❌ Missing Data Issues:")
        for issue, count in issues['missing_data'].items():
            print(f"   {issue}: {count}")
            total_issues += count
        
        print("\n🔄 Duplicate Issues:")
        for issue, count in issues['duplicates'].items():
            print(f"   {issue}: {count}")
            total_issues += count
        
        print("\n📊 Outlier Issues:")
        for issue, count in issues['outliers'].items():
            print(f"   {issue}: {count}")
            total_issues += count if issue != 'text_length_outliers' else 0
        
        print("\n⚠️  Inconsistency Issues:")
        for issue, count in issues['inconsistencies'].items():
            print(f"   {issue}: {count}")
            total_issues += count
        
        if total_issues == 0:
            print("\n✅ No major data quality issues detected!")
        else:
            print(f"\n🚨 Total issues found: {total_issues}")
    
    def generate_recommendations(self) -> List[str]:
        """Generate data preprocessing recommendations"""
        recommendations = []
        
        if not hasattr(self, 'stats'):
            self.basic_statistics()
        
        # Text length recommendations
        mean_length = self.stats['text_length']['mean']
        max_length = self.stats['text_length']['max']
        
        if max_length > 1000:
            recommendations.append(f"📏 Consider truncating texts to 512-1024 characters (current max: {max_length:.0f})")
        
        if mean_length < 50:
            recommendations.append("📝 Texts are quite short - consider concatenating or using smaller models")
        
        # Class balance recommendations
        imbalance_ratio = max(self.stats['label_distribution'].values()) / min(self.stats['label_distribution'].values())
        if imbalance_ratio > 3:
            recommendations.append(f"⚖️  Dataset is imbalanced (ratio: {imbalance_ratio:.1f}) - consider oversampling, undersampling, or class weights")
        
        # Dataset size recommendations
        total_samples = self.stats['total_samples']
        if total_samples < 1000:
            recommendations.append("📊 Small dataset - consider data augmentation or transfer learning")
        elif total_samples > 100000:
            recommendations.append("📊 Large dataset - consider sampling for faster experimentation")
        
        # Vocabulary recommendations
        if hasattr(self, 'vocab_stats'):
            diversity = self.vocab_stats.get('vocabulary_diversity', 0)
            if diversity > 0.8:
                recommendations.append("📚 High vocabulary diversity - consider preprocessing to reduce noise")
        
        if not recommendations:
            recommendations.append("✅ Dataset looks good for BERT fine-tuning!")
        
        return recommendations
    
    def full_analysis(self) -> Dict:
        """Run complete data analysis"""
        print("🚀 Starting comprehensive data analysis...")
        
        results = {}
        results['basic_stats'] = self.basic_statistics()
        results['quality_analysis'] = self.text_quality_analysis()
        results['vocab_analysis'] = self.vocabulary_analysis()
        results['label_analysis'] = self.label_distribution_analysis()
        results['data_issues'] = self.detect_data_issues()
        
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS")
        print("="*70)
        
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"{i:2d}. {rec}")
        
        results['recommendations'] = recommendations
        
        print("\n✅ Data analysis complete!")
        return results

class DataCleaner:
    """Data cleaning and preprocessing utilities"""
    
    def __init__(self, df: pd.DataFrame, text_column: str, label_column: str):
        self.df = df.copy()
        self.text_column = text_column
        self.label_column = label_column
        self.cleaning_log = []
    
    def remove_duplicates(self, keep_first: bool = True) -> pd.DataFrame:
        """Remove duplicate entries"""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=[self.text_column], keep='first' if keep_first else 'last')
        removed_count = initial_count - len(self.df)
        
        self.cleaning_log.append(f"Removed {removed_count} duplicate texts")
        print(f"🔄 Removed {removed_count} duplicates ({len(self.df)} samples remaining)")
        return self.df
    
    def remove_missing_data(self) -> pd.DataFrame:
        """Remove rows with missing text or labels"""
        initial_count = len(self.df)
        
        # Remove missing text
        self.df = self.df.dropna(subset=[self.text_column])
        
        # Remove missing labels
        self.df = self.df.dropna(subset=[self.label_column])
        
        # Remove empty text
        self.df = self.df[self.df[self.text_column].str.strip() != '']
        
        removed_count = initial_count - len(self.df)
        self.cleaning_log.append(f"Removed {removed_count} rows with missing data")
        print(f"❌ Removed {removed_count} rows with missing data ({len(self.df)} samples remaining)")
        return self.df
    
    def filter_by_length(self, min_length: int = 10, max_length: int = 5000) -> pd.DataFrame:
        """Filter texts by character length"""
        initial_count = len(self.df)
        
        self.df['text_length'] = self.df[self.text_column].str.len()
        self.df = self.df[(self.df['text_length'] >= min_length) & (self.df['text_length'] <= max_length)]
        
        removed_count = initial_count - len(self.df)
        self.cleaning_log.append(f"Filtered by length {min_length}-{max_length}: removed {removed_count} texts")
        print(f"📏 Filtered by length {min_length}-{max_length}: removed {removed_count} texts ({len(self.df)} samples remaining)")
        return self.df
    
    def clean_text(self, remove_html: bool = True, remove_urls: bool = True, 
                   remove_emails: bool = True, remove_phone: bool = True,
                   normalize_whitespace: bool = True) -> pd.DataFrame:
        """Apply text cleaning operations"""
        print("🧹 Applying text cleaning operations...")
        
        for idx, text in enumerate(self.df[self.text_column]):
            if pd.isna(text):
                continue
                
            original_text = str(text)
            
            # Remove HTML tags
            if remove_html:
                original_text = re.sub(r'<[^>]+>', '', original_text)
            
            # Remove URLs
            if remove_urls:
                original_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', original_text)
                original_text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', original_text)
            
            # Remove emails
            if remove_emails:
                original_text = re.sub(r'\S+@\S+', '', original_text)
            
            # Remove phone numbers
            if remove_phone:
                original_text = re.sub(r'\d{3}-?\d{3}-?\d{4}', '', original_text)
            
            # Normalize whitespace
            if normalize_whitespace:
                original_text = ' '.join(original_text.split())
            
            self.df.iloc[idx, self.df.columns.get_loc(self.text_column)] = original_text
        
        self.cleaning_log.append("Applied text cleaning operations")
        print("✅ Text cleaning completed")
        return self.df
    
    def balance_classes(self, method: str = 'undersample', target_size: int = None) -> pd.DataFrame:
        """Balance class distribution"""
        label_counts = self.df[self.label_column].value_counts()
        print(f"📊 Current class distribution: {dict(label_counts)}")
        
        if method == 'undersample':
            # Undersample to smallest class size
            min_count = label_counts.min() if target_size is None else target_size
            balanced_dfs = []
            
            for label in label_counts.index:
                label_df = self.df[self.df[self.label_column] == label].sample(n=min_count, random_state=42)
                balanced_dfs.append(label_df)
            
            self.df = pd.concat(balanced_dfs, ignore_index=True).sample(frac=1, random_state=42)
            
        elif method == 'oversample':
            # Oversample to largest class size (simple duplication)
            max_count = label_counts.max() if target_size is None else target_size
            balanced_dfs = []
            
            for label in label_counts.index:
                label_df = self.df[self.df[self.label_column] == label]
                
                if len(label_df) < max_count:
                    # Repeat samples to reach target size
                    repeats = max_count // len(label_df)
                    remainder = max_count % len(label_df)
                    
                    repeated_df = pd.concat([label_df] * repeats, ignore_index=True)
                    if remainder > 0:
                        extra_samples = label_df.sample(n=remainder, random_state=42)
                        repeated_df = pd.concat([repeated_df, extra_samples], ignore_index=True)
                    
                    balanced_dfs.append(repeated_df)
                else:
                    balanced_dfs.append(label_df)
            
            self.df = pd.concat(balanced_dfs, ignore_index=True).sample(frac=1, random_state=42)
        
        new_counts = self.df[self.label_column].value_counts()
        print(f"⚖️  Balanced class distribution: {dict(new_counts)}")
        self.cleaning_log.append(f"Applied {method} class balancing")
        
        return self.df
    
    def get_cleaning_summary(self) -> List[str]:
        """Get summary of all cleaning operations performed"""
        return self.cleaning_log.copy()

# Example usage function
def demo_data_exploration():
    """Demonstrate data exploration capabilities"""
    print("="*70)
    print("🔍 DATA EXPLORATION DEMO")
    print("="*70)
    
    # Create sample data
    sample_data = {
        'text': [
            "This is a great product! I love it so much.",
            "Terrible service, very disappointed with the quality.",
            "Average item, nothing special but works as expected.",
            "Outstanding performance, highly recommend to everyone!",
            "Poor build quality, broke after one day of use.",
            "Excellent customer service and fast delivery.",
            "Not worth the money, better alternatives available.",
            "Perfect for my needs, exactly what I was looking for.",
            "Decent quality but overpriced for what you get.",
            "Amazing features and great value for money!"
        ] * 50,  # Multiply to get more samples
        'label': ([1, 0, 1, 1, 0, 1, 0, 1, 0, 1] * 50)  # 1=positive, 0=negative
    }
    
    df = pd.DataFrame(sample_data)
    
    # Run exploration
    explorer = DataExplorer(df, 'text', 'label')
    results = explorer.full_analysis()
    
    # Demonstrate cleaning
    print("\n" + "="*70)
    print("🧹 DATA CLEANING DEMO")
    print("="*70)
    
    cleaner = DataCleaner(df, 'text', 'label')
    
    # Add some problematic data for demonstration
    df_with_issues = df.copy()
    df_with_issues.loc[len(df_with_issues)] = ['', 1]  # Empty text
    df_with_issues.loc[len(df_with_issues)] = ['Check out http://example.com for more info!', 1]  # URL
    df_with_issues.loc[len(df_with_issues)] = [df_with_issues.iloc[0]['text'], 1]  # Duplicate
    
    cleaner_demo = DataCleaner(df_with_issues, 'text', 'label')
    cleaned_df = cleaner_demo.remove_missing_data()
    cleaned_df = cleaner_demo.clean_text()
    cleaned_df = cleaner_demo.remove_duplicates()
    
    print(f"\n📋 Cleaning Summary:")
    for operation in cleaner_demo.get_cleaning_summary():
        print(f"   • {operation}")
    
    print("\n✅ Data exploration and cleaning demo complete!")

if __name__ == "__main__":
    demo_data_exploration()
