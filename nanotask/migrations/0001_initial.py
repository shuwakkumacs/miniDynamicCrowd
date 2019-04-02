# Generated by Django 2.0.7 on 2019-04-02 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AMTAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mturk_assignment_id', models.CharField(max_length=255)),
                ('mturk_hit_id', models.CharField(blank=True, max_length=255, null=True)),
                ('mturk_worker_id', models.CharField(blank=True, max_length=255, null=True)),
                ('bonus_amount', models.FloatField(default=0.0)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_bonus_sent', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('value', models.TextField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HIT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mturk_hit_id', models.CharField(max_length=255)),
                ('project_name', models.CharField(max_length=255)),
                ('is_sandbox', models.IntegerField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_expired', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Nanotask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.TextField(max_length=255)),
                ('template_name', models.TextField(max_length=255)),
                ('media_data', models.TextField(blank=True, default='{}')),
                ('create_id', models.CharField(max_length=100)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mturk_worker_id', models.CharField(blank=True, max_length=255, null=True)),
                ('session_tab_id', models.CharField(max_length=32)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_assigned', models.DateTimeField(blank=True, null=True)),
                ('time_submitted', models.DateTimeField(blank=True, null=True)),
                ('working_time', models.FloatField(default=0.0)),
                ('user_agent', models.CharField(max_length=255)),
                ('amt_assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nanotask.AMTAssignment')),
                ('nanotask', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nanotask.Nanotask')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nanotask.Ticket'),
        ),
    ]
