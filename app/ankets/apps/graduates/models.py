from django.db import models

# Create your models here.
class Spravochnik(models.Model):
    spravochnik_number = models.IntegerField("код справочника с ответами")
    spravochnik_kod = models.IntegerField("код ответа")
    spravochnik_name = models.CharField("наименование", max_length=255, null=True)
    def __str__(self):
        return self.spravochnik_name
    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'

class Respondent(models.Model):
    respondent_type = models.IntegerField("тип респондента")
    respondent_name = models.CharField("название типа респондента", max_length=100)
    def __str__(self):
        return self.respondent_name
    class Meta:
        verbose_name = 'Респондент'
        verbose_name_plural = 'Респонденты'

class Questionblock(models.Model):
    block_number = models.IntegerField("номер блока")
    respondent_type = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    block_name = models.TextField("название блока вопросов", null=True)
    block_type = models.IntegerField("тип блока вопросов (обычные или таблица с возможностью добавления)", null=True)
    essance_label = models.TextField("кого (что) добавляем", null=True)
    def __str__(self):
        return self.block_name
    class Meta:
        verbose_name = 'Блок вопросов'
        verbose_name_plural = 'Блоки вопросов'
        unique_together = ('block_number', 'respondent_type')

class Question(models.Model):
    respondent_type = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    block_number = models.ForeignKey(Questionblock, on_delete=models.DO_NOTHING)
    question_number = models.IntegerField("номер вопроса")
    question_name = models.TextField("вопрос", null=True)
    question_clarification = models.TextField("пояснение к вопросу", null=True)
    question_type = models.IntegerField("тип вопроса", null=True) #открытый вопрос/закрытый вопрос
    field_type = models.TextField("тип поля свободного ответа (текст/число)", default='text', null=True)
    field_mask = models.TextField("маска ввода", null=True)
    field_placeholder = models.TextField("подпись к полю", null=True)
    field_required = models.IntegerField("обязательность заполнения (0-нет, 1-да)", null=True)
    def __str__(self):
        return self.question_name
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        unique_together = ('respondent_type', 'block_number', 'question_number')

class Answer(models.Model):
    respondent_type = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    block_number = models.ForeignKey(Questionblock, on_delete=models.DO_NOTHING)
    question_number = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    answer_number = models.IntegerField("номер ответа")
    answer_name = models.TextField("ответ", null=True)
    answer_type = models.IntegerField("тип ответа", null=True) #отдельный тип для вариантов ответов из справочника?
    answer_spravochnik = models.IntegerField("код справочника с ответами", null=True)
    def __str__(self):
        return self.answer_name
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        unique_together = ('respondent_type', 'block_number', 'question_number', 'answer_number')

class Result(models.Model):
    respondent_type = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    block_number = models.ForeignKey(Questionblock, on_delete=models.DO_NOTHING)
    question_number = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    essence_id = models.IntegerField("номер выпускника/работодателя (для вопросов с возможностью добавления строк)", default=0, null=True)
    result_result = models.IntegerField("ответ", null=True)
    respondent_id = models.CharField("уникальный код респондента", max_length=100)
    result_free = models.TextField("свободный ответ", null=True)
    result_date = models.DateTimeField("дата заполнения")
    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'

class Raw(models.Model):
    respid = models.CharField("уникальный код респондента", max_length=100)
    datapost = models.TextField("исходник данных", null=True)
    result_date = models.DateTimeField("дата заполнения")
    def __str__(self):
        return self.datapost

class Links(models.Model):
    respondent_type = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    respondent_id = models.CharField("уникальный код респондента", max_length=100)
    status = models.IntegerField("статус анкеты")
    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
    # def __str__(self):
    #     return self.respondent_type