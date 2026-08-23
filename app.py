import cv2

# 1. قراءة الصورة الأصلية
image_path = "original_image.jpg"  # ضع اسم ملف صورتك هنا
img = cv2.imread(image_path)

# 2. الحصول على أبعاد الصورة (الارتفاع والعرض)
height, width, _ = img.shape

# 3. تحديد نقطة القص (إزالة النصف السفلي الذي يحتوي على الجدول)
# قمنا بتحديد 30% من الارتفاع للاحتفاظ بالملخص العلوي فقط
crop_height = int(height * 0.30)
cropped_img = img[0:crop_height, 0:width]

# 4. حفظ الصورة الجديدة الناتجة
output_path = "cleared_image.jpg"
cv2.imwrite(output_path, cropped_img)

print("تم مسح الصندوق وحفظ الصورة بنجاح!")
