from PIL import Image

# 1. قراءة الصورة الأصلية
image_path = "original_image.jpg"  # ضع اسم ملف صورتك هنا
img = Image.open(image_path)

# 2. الحصول على أبعاد الصورة
width, height = img.size

# 3. تحديد منطقة القص (الاحتفاظ بأول 30% من الارتفاع)
crop_height = int(height * 0.30)
# الأبعاد المحددة للقص: (اليسار، الأعلى، اليمين، الأسفل)
cropped_img = img.crop((0, 0, width, crop_height))

# 4. حفظ الصورة الجديدة الناتجة
output_path = "cleared_image.jpg"
cropped_img.save(output_path)

print("تم مسح الصندوق وحفظ الصورة بنجاح باستخدام PIL!")
